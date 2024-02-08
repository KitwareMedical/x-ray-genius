from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from uuid import uuid4

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.files import File

from .models import OutputImage, Session

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

    # Parameters
    source_to_detector_distance: float = session.parameters.source_to_detector_distance
    carm_alpha: int = session.parameters.carm_alpha
    carm_beta: int = session.parameters.carm_beta

    # Initialize the C-arm object
    carm = MobileCArm(source_to_detector_distance=source_to_detector_distance)

    # Initialize the Projector object (allocates GPU memory)
    with Projector(ct, carm=carm) as projector:
        # Orient and position the patient model in world space.
        ct.orient_patient(head_first=True, supine=True)
        ct.place_center(carm.isocenter_in_world)

        # Move the C-arm to the desired pose.
        carm.move_to(alpha=carm_alpha, beta=carm_beta, degrees=True)

        # Run projection
        image = projector()

    with TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / 'image.png'
        image_utils.save(dest, image)
        img = File(BytesIO(dest.read_bytes()), name=f'{uuid4()}.png')
        output_image = OutputImage.objects.create(file=img, session=session)

    Session.objects.filter(pk=session_pk).update(status=Session.Status.PROCESSED)
    logger.info(f'Created output image {output_image.pk} for session {session_pk}')
