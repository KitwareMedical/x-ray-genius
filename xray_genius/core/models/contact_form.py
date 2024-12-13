from django.db import models
from django_extensions.db.fields import CreationDateTimeField


class ContactFormSubmission(models.Model):
    created = CreationDateTimeField()

    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self) -> str:
        return f'From {self.name} <{self.email}>'
