from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from uuid import uuid4

from PIL import Image
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.files import File

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

    with NamedTemporaryFile() as f:
        f.write(session.input_scan.file.read())
        if session.input_scan.file.name.endswith('.nrrd'):
            ct = Volume.from_nrrd(f.name)
        else:
            ct = Volume.from_dicom(f.name)

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
