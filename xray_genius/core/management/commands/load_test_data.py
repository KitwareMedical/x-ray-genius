from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.core.files import File
from django.core.management import call_command
from django.db import models, transaction
import djclick as click
from girder_client import GirderClient

from xray_genius.core.models import SampleDataset, SampleDatasetFile

GIRDER_API_URL = 'https://data.kitware.com/api/v1'


# Map sample dataset file PK (from xray_genius/core/fixtures/sampledata.json) to DKC collection id
DKC_SAMPLE_DATASETS: dict[int, str] = {
    1: '68dc2b793ba8f1c07a875e7a',
    2: '68dc2b973ba8f1c07a875e80',
}


@click.command()
def load_test_data() -> None:
    gc = GirderClient(apiUrl=GIRDER_API_URL)

    call_command('loaddata', 'sampledata')

    for sample_dataset in SampleDataset.objects.iterator():
        click.echo(f'Creating test data for "{sample_dataset.name}"...')
        sample_dataset_files: models.QuerySet[SampleDatasetFile] = sample_dataset.files.all()

        sample_dataset_file: SampleDatasetFile
        for sample_dataset_file in sample_dataset_files.iterator():
            with NamedTemporaryFile() as tmp_file:
                click.echo(
                    click.style(
                        f'  Downloading "{sample_dataset.name}" test data from DKC...', fg='cyan'
                    ),
                    nl=False,
                )
                gc.downloadFile(
                    fileId=DKC_SAMPLE_DATASETS[sample_dataset_file.pk], path=tmp_file.name
                )
                click.echo(click.style('  done', fg='green'))

                with transaction.atomic():
                    sample_dataset_file_locked = SampleDatasetFile.objects.select_for_update().get(
                        pk=sample_dataset_file.pk
                    )
                    sample_dataset_file_locked.file = File(
                        BytesIO(Path(tmp_file.name).read_bytes()), name=sample_dataset_file.name
                    )
                    sample_dataset_file_locked.save()

    click.echo(click.style('Done!', fg='green'))
