from captcha.fields import CaptchaField
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import ContactFormSubmission, CTInputFile


class CTInputFileUploadForm(ModelForm):
    class Meta:
        model = CTInputFile
        fields = ['file']


class ContactForm(ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = ContactFormSubmission
        fields = ['name', 'email', 'message']

    def __init__(self, *args, user: User | None, **kwargs):
        super().__init__(*args, **kwargs)

        # If the user is logged in, don't show the captcha
        if user is not None:
            del self.fields['captcha']
