from datetime import timedelta
from io import BytesIO
from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile, TemporaryDirectory
from uuid import uuid4
from zipfile import ZipFile

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from django.core.files.base import ContentFile, File
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import QuerySet
from django.template.loader import render_to_string
import sentry_sdk

from .models import ContactFormSubmission, OutputImage, Session
from .models.input_parameters import DEFAULT_SENSOR_SIZE
from .notifications import TaskTracker
from .utils import ParameterSampler

logger = get_task_logger(__name__)


@shared_task(
    soft_time_limit=timedelta(minutes=10).total_seconds(),
)
def run_deepdrr_task(session_pk: str) -> None:
    try:
        with transaction.atomic():
            # First, lock the session and ensure it's in the proper state.
            # Then, before releasing the lock, update the state.
            # This is done to prevent race conditions if this task is executed
            # multiple times concurrently, which is always a possibility due to
            # us using `acks_late` in Celery.
            session = Session.objects.select_for_update().get(pk=session_pk)
            if session.status != Session.Status.QUEUED:
                logger.error('Session %s is not queued, aborting processing', session_pk)
                return
            session.status = Session.Status.RUNNING
            session.save()
        # Refetch the session without the lock with joined data
        session = Session.objects.select_related('parameters', 'input_scan').get(pk=session_pk)
    except Session.DoesNotExist:
        logger.info('Session %s was deleted, aborting processing', session_pk)
        return

    # Import here to avoid attempting to load CUDA on the web server
    from deepdrr import MobileCArm, Volume, geo
    from deepdrr.projector import Projector  # separate import for CUDA init
    import numpy as np
    from PIL import Image
    import png
    from scipy.spatial.transform import Rotation

    def to_supine(ct: Volume):
        """
        Turn the volume to be face up.

        This aligns the patient so that, in world space,
        the anterior side is toward +Z, inferior is toward +X,
        and left is toward +Y.

        Raises:
            NotImplementedError: If the anatomical coordinate system is not "RAS" or "LPS".

        """
        if ct.anatomical_coordinate_system == 'RAS':
            ct.world_from_anatomical = geo.FrameTransform.from_rt(
                rotation=Rotation.from_euler('xz', [90, -90], degrees=True).as_matrix().squeeze(),
            )
        elif ct.anatomical_coordinate_system == 'LPS':
            ct.world_from_anatomical = geo.FrameTransform.from_rt(
                rotation=Rotation.from_euler('xz', [-90, 90], degrees=True).as_matrix().squeeze(),
            )
        else:
            raise NotImplementedError(
                f'Cannot handle anatomical coordinate system {ct.anatomical_coordinate_system}'
            )

    state = {'type': 'session_update', 'session_pk': str(session_pk)}
    tracker = TaskTracker(state=state, group_names=[f'dashboard_{session.owner.pk}'])
    with tracker.running():
        tracker.description = 'Reading input file'
        tracker.flush()

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
            source_to_isocenter_vertical_distance=source_to_detector_distance / 2,
            sensor_height=DEFAULT_SENSOR_SIZE,
            sensor_width=DEFAULT_SENSOR_SIZE,
            pixel_size=session.parameters.sensor_pixel_pitch,
            min_alpha=-180,
            max_alpha=180,
            min_beta=-180,
            max_beta=180,
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
                    logger.info('Session %s was cancelled', session_pk)
                    OutputImage.objects.filter(session=session).delete()
                    Session.objects.filter(pk=session_pk).update(status=Session.Status.NOT_STARTED)
                    return

                tracker.progress = i / param_sampler.samples
                tracker.description = f'Generating image {i + 1} of {param_sampler.samples}'
                tracker.flush(max_rate_seconds=0.5)
                logger.info(
                    'Running DeepDRR for session %s (%d/%d)',
                    session_pk,
                    i + 1,
                    param_sampler.samples,
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
                    name = uuid4()

                    if image.dtype in (np.float16, np.float32, np.float64):
                        image_u16 = np.clip(image * 0xFFFF, 0, 0xFFFF).astype(np.uint16)
                        image_u8 = np.clip(image * 0xFF, 0, 0xFF).astype(np.uint8)
                    else:
                        logger.warning('Naive cast image %r (unknown dtype %r).', name, image.dtype)
                        image_u16 = image.astype(np.uint16)
                        image_u8 = image.astype(np.uint8)

                    png.from_array(image_u16, mode='L;16').save(dest)
                    img = File(BytesIO(dest.read_bytes()), name=f'{name}.png')

                    thumbnail_dest = Path(tmpdir) / 'thumbnail.png'
                    thumbnail_img = Image.fromarray(image_u8)
                    thumbnail_img.thumbnail((64, 64))
                    thumbnail_img.save(thumbnail_dest)
                    thumbnail = File(
                        BytesIO(thumbnail_dest.read_bytes()), name=f'{name}_thumbnail.png'
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
        logger.info('Created output image %s for session %s', output_image.pk, session_pk)

    zip_images_task.delay(session_pk)


@shared_task(soft_time_limit=30)
def zip_images_task(session_pk: str) -> None:
    session = Session.objects.get(pk=session_pk)

    with NamedTemporaryFile() as buffer:
        with ZipFile(buffer.name, 'w') as zip_file:
            output_images: QuerySet[OutputImage] = session.output_images.all()
            for output_image in output_images.iterator():
                image_name = Path(output_image.image.name).name

                # Preserve bit-depth. Do not use Image.open.
                with output_image.image.open('rb') as src, NamedTemporaryFile() as dst:
                    shutil.copyfileobj(src, dst)
                    zip_file.write(filename=dst.name, arcname=image_name)

        with NamedTemporaryFile() as zip_output:
            buffer.seek(0)
            zip_output.write(buffer.read())
            buffer.seek(0)
            session.output_images_zip.save('images.zip', ContentFile(buffer.read()), save=True)

    logger.info('Created zip file for session %s', session_pk)


@shared_task(soft_time_limit=60)
def delete_session_task(session_pk: str) -> None:
    # This delete query will also trigger a bunch of Django signals
    # that make DELETE calls to S3, so we do this in an async task.
    Session.objects.filter(pk=session_pk).delete()
    logger.info('Deleted session %s', session_pk)


@shared_task
def send_contact_form_submission_to_admins_task(contact_form_submission_pk: int) -> None:
    form_submission = ContactFormSubmission.objects.get(pk=contact_form_submission_pk)

    admin_emails = User.objects.filter(is_superuser=True, is_active=True).values_list(
        'email', flat=True
    )  # TODO: add kitware@kitware.com once this is tested

    subject = '[xray-genius] New contact form submission'
    message = render_to_string(
        template_name='contact_form_submission_email.txt',
        context={'form_submission': form_submission},
    )

    EmailMessage(subject=subject, body=message, to=admin_emails).send(fail_silently=False)


@shared_task
def check_for_stuck_sessions_beat() -> None:
    """
    Check for stuck sessions and send a Sentry alert if any are found.

    A "stuck" session is defined as a session that has been either sitting in the
    queue, or in the running state, for longer than the session timeout. This can
    happen if the Celery worker that was processing the session died, or if there
    is a bug in the code that causes the session to exit before it can update its
    status.
    """
    stuck_sessions = Session.stuck_objects.all().count()

    if stuck_sessions > 0:
        logger.info('Found %s stuck sessions', stuck_sessions)
        sentry_sdk.capture_message(
            f'Found {stuck_sessions} stuck sessions!! Manual intervention required.'
        )
