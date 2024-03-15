from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from uuid import uuid4
from zipfile import ZipFile

from PIL import Image
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.files.base import ContentFile, File
from django.db.models import QuerySet

from .models import OutputImage, Session
from .utils import ParameterSampler

logger = get_task_logger(__name__)


@shared_task
def run_deepdrr_task(session_pk: str) -> None:
    # Import here to avoid attempting to load CUDA on the web server
    from deepdrr import MobileCArm, Volume
    from deepdrr.projector import Projector  # separate import for CUDA init
    from deepdrr.utils import image_utils

    session = Session.objects.select_related('parameters', 'input_scan').get(pk=session_pk)

    with TemporaryDirectory() as f:
        dest = Path(f) / f'temp.{".".join(session.input_scan.file.name.split(".")[1:]).lower()}'
        dest.write_bytes(session.input_scan.file.read())
        if dest.suffix == '.nrrd':
            ct = Volume.from_nrrd(dest)
        elif dest.suffix == '.dcm':
            ct = Volume.from_dicom(
                dest,
                # TODO: remove this when the cache_dir is set correctly upstream.
                cache_dir=dest.parent / 'cache',
            )
        else:
            ct = Volume.from_nifti(dest)

    source_to_detector_distance: float = session.parameters.source_to_detector_distance

    carm = MobileCArm(source_to_detector_distance=source_to_detector_distance)

    param_sampler = ParameterSampler(session.parameters)

    # Initialize the Projector object (allocates GPU memory)
    with Projector(ct, carm=carm) as projector:
        for (
            push_pull,
            head_foot_translation,
            raise_lower,
            alpha,
            beta,
        ) in zip(
            param_sampler.carm_push_pull,
            param_sampler.carm_head_foot_translation,
            param_sampler.carm_raise_lower,
            param_sampler.carm_alpha,
            param_sampler.carm_beta,
            strict=True,
        ):
            session.refresh_from_db(fields=['status'])
            if session.status == Session.Status.CANCELLED:
                logger.info(f'Session {session_pk} was cancelled')
                OutputImage.objects.filter(session=session).delete()
                return

            carm.move_to(alpha=alpha, beta=beta, degrees=True)

            image = projector()

            with TemporaryDirectory() as tmpdir:
                dest = Path(tmpdir) / 'image.png'
                image_utils.save(dest, image)
                img = File(BytesIO(dest.read_bytes()), name=f'{uuid4()}.png')

                thumbnail_dest = Path(tmpdir) / 'thumbnail.png'
                thumnail_img = Image.open(dest)
                thumnail_img.thumbnail((64, 64))
                thumnail_img.save(thumbnail_dest)
                thumbnail = File(
                    BytesIO(thumbnail_dest.read_bytes()), name=f'{uuid4()}_thumbnail.png'
                )

                output_image = OutputImage.objects.create(
                    image=img,
                    thumbnail=thumbnail,
                    session=session,
                    carm_push_pull=push_pull,
                    carm_head_foot_translation=head_foot_translation,
                    carm_raise_lower=raise_lower,
                    carm_alpha=alpha,
                    carm_beta=beta,
                )

    Session.objects.filter(pk=session_pk).update(status=Session.Status.PROCESSED)
    logger.info(f'Created output image {output_image.pk} for session {session_pk}')

    zip_images_task.delay(session_pk)


@shared_task
def zip_images_task(session_pk: str) -> None:
    session = Session.objects.get(pk=session_pk)

    with NamedTemporaryFile() as buffer:
        with ZipFile(buffer.name, 'w') as zip_file:
            output_images: QuerySet[OutputImage] = session.output_images.all()
            for output_image in output_images.iterator():
                image_name = Path(output_image.image.name).name

                with Image.open(output_image.image) as img:
                    with TemporaryDirectory() as tmpdir:
                        image_name = Path(tmpdir) / image_name
                        img.save(image_name)
                        zip_file.write(filename=image_name, arcname=image_name.name)

        with NamedTemporaryFile() as zip_output:
            buffer.seek(0)
            zip_output.write(buffer.read())
            buffer.seek(0)
            session.output_images_zip.save('images.zip', ContentFile(buffer.read()), save=True)

    logger.info(f'Created zip file for session {session_pk}')
