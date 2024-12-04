from io import BytesIO
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.files import File
from django.core.management import call_command
from django.db import transaction
import djclick as click
from girder_client import GirderClient

from xray_genius.core.models import OutputImage, Session
from xray_genius.core.tasks import zip_images_task

GIRDER_API_URL = 'https://data.kitware.com/api/v1'
GIRDER_FILE_ID = '65dfa5cccc95b227463a2475'


@click.command()
@click.argument('girder_api_key', envvar='GIRDER_API_KEY')
def load_test_data(girder_api_key: str) -> None:
    gc = GirderClient(apiUrl=GIRDER_API_URL)
    gc.authenticate(apiKey=girder_api_key)

    user = User.objects.filter(id=1).first()

    if not user:
        raise ValueError(
            click.style(
                'User with id=1 does not exist, please create one in the admin console.', fg='red'
            )
        )

    click.echo(f'Creating test sessions for {user.email}')
    call_command('loaddata', 'testdata')

    with TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path(tmp_dir)
        extracted_dir = tmp_dir_path / 'testdata'
        click.echo(click.style('Downloading test data from DKC...', fg='cyan'), nl=False)
        gc.downloadFile(fileId=GIRDER_FILE_ID, path=str(tmp_dir_path / 'testdata.tar'))
        click.echo(click.style('done', fg='green'))
        with tarfile.open(tmp_dir_path / 'testdata.tar', 'r') as tar:
            (tmp_dir_path / 'testdata').mkdir()
            tar.extractall(extracted_dir)  # noqa: S202
        for session_dir in extracted_dir.iterdir():
            click.echo(f'Processing session {click.style(session_dir.name, fg="yellow")}...')
            with transaction.atomic():
                session = Session.objects.get(pk=session_dir.name)
                ct_scan = next(f for f in session_dir.iterdir() if f.is_file())
                input_ct = File(BytesIO(ct_scan.read_bytes()), name=ct_scan.name)
                session.input_scan.file = input_ct
                session.save()
                for image in (session_dir / 'images').iterdir():
                    click.echo(f'\tProcessing image {click.style(image.name, fg="magenta")}...')
                    output_image = OutputImage.objects.get(pk=image.stem)
                    assert image.is_file()
                    django_img = File(BytesIO(image.read_bytes()), name=f'{uuid4()}.png')
                    output_image.image = django_img
                    output_image.save()
                for thumbnail in (session_dir / 'thumbnails').iterdir():
                    click.echo(
                        f'\tProcessing thumbnail {click.style(thumbnail.name, fg="blue")}...'
                    )
                    output_image = OutputImage.objects.get(pk=thumbnail.stem)
                    assert thumbnail.is_file()
                    thumbnail_img = File(
                        BytesIO(thumbnail.read_bytes()),
                        name=f'{uuid4()}.png',
                    )
                    output_image.thumbnail = thumbnail_img
                    output_image.save()

    zip_images_task.delay(str(Session.objects.first().pk))

    click.echo(click.style('Done!', fg='green'))
