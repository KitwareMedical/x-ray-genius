from django.forms import ModelForm

from .models import ContactFormSubmission, CTInputFile


class CTInputFileUploadForm(ModelForm):
    class Meta:
        model = CTInputFile
        fields = ['file']


class ContactForm(ModelForm):
    class Meta:
        model = ContactFormSubmission
        fields = ['name', 'email', 'message']
