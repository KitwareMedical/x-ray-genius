from django.forms import ModelForm

from .models import CTInputFile


class CTInputFileUploadForm(ModelForm):
    class Meta:
        model = CTInputFile
        fields = ['file']
