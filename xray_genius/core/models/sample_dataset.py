from django.db import models


class SampleDataset(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    license = models.TextField()
    source = models.TextField()

    def __str__(self) -> str:
        return self.name


class SampleDatasetFile(models.Model):
    sample_dataset = models.ForeignKey(
        SampleDataset, on_delete=models.CASCADE, related_name='files'
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='sample_data')
