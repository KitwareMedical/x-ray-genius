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
from .models.input_parameters import DEFAULT_SENSOR_SIZE
from .utils import ParameterSampler

logger = get_task_logger(__name__)


@shared_task
def run_deepdrr_task(session_pk: str) -> None:
    # Import here to avoid attempting to load CUDA on the web server
    from deepdrr import MobileCArm, Volume, geo
    from deepdrr.projector import Projector  # separate import for CUDA init
    from deepdrr.utils import image_utils
    from scipy.spatial.transform import Rotation

    def to_supine(ct: Volume):
        """Turns the volume to be face up.

        This aligns the patient so that, in world space,
        the anterior side is toward +Z, inferior is toward +X,
        and left is toward +Y.

        Raises:
            NotImplementedError: If the anatomical coordinate system is not "RAS" or "LPS".

        """
        if ct.anatomical_coordinate_system == 'RAS':
            ct.world_from_anatomical = geo.FrameTransform.from_rt(
                rotation=Rotation.from_euler("xz", [90, -90], degrees=True).as_matrix().squeeze(),
            )
        elif ct.anatomical_coordinate_system == 'LPS':
            ct.world_from_anatomical = geo.FrameTransform.from_rt(
                rotation=Rotation.from_euler("xz", [-90, 90], degrees=True).as_matrix().squeeze(),
            )
        else:
            raise NotImplementedError(
                f'Cannot handle anatomical coordinate system {ct.anatomical_coordinate_system}'
            )

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

    # place CT at center of the world, oriented supine (ILA)
    to_supine(ct)
    ct.place_center(geo.p(0, 0, 0))

    source_to_detector_distance: float = session.parameters.source_to_detector_distance

    carm = MobileCArm(
        source_to_detector_distance=source_to_detector_distance,
        sensor_height=DEFAULT_SENSOR_SIZE,
        sensor_width=DEFAULT_SENSOR_SIZE,
        pixel_size=session.parameters.sensor_pixel_pitch,
    )

    param_sampler = ParameterSampler(session.parameters)

    # Initialize the Projector object (allocates GPU memory)
    with Projector(ct, carm=carm) as projector:
        for i, (
            push_pull_translation,
            head_foot_translation,
            raise_lower_translation,
            alpha,
            beta,
        ) in enumerate(
            zip(
                param_sampler.carm_push_pull_translation,
                param_sampler.carm_head_foot_translation,
                param_sampler.carm_raise_lower_translation,
                param_sampler.carm_alpha,
                param_sampler.carm_beta,
                strict=True,
            )
        ):
            session.refresh_from_db(fields=['status'])
            if session.status == Session.Status.CANCELLED:
                logger.info(f'Session {session_pk} was cancelled')
                OutputImage.objects.filter(session=session).delete()
                return

            logger.info(
                f'Running DeepDRR for session {session_pk} (Image {i + 1}/{param_sampler.samples})'
            )

            carm.move_to(
                alpha=alpha,
                beta=beta,
                degrees=True,
                isocenter=geo.p(
                    # incoming parameters are in LPS, but deepdrr supine
                    # is in ILA (-Z, +X, -Y).
                    # head_foot: +Z, push_pull: +X, raise_lower: +Y
                    -head_foot_translation,
                    push_pull_translation,
                    -raise_lower_translation,
                ),
            )

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
                    carm_push_pull=push_pull_translation,
                    carm_head_foot_translation=head_foot_translation,
                    carm_raise_lower=raise_lower_translation,
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


@shared_task
def delete_session_task(session_pk: str) -> None:
    # This delete query will also trigger a bunch of Django signals
    # that make DELETE calls to S3, so we do this in an async task.
    Session.objects.filter(pk=session_pk).delete()
    logger.info(f'Deleted session {session_pk}')
