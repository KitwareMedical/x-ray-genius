from allauth.account.signals import user_signed_up
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models.base import ModelBase
from django.dispatch import receiver
from django.template.loader import render_to_string


@receiver(user_signed_up)
def user_signed_up_listener(*, sender: ModelBase, user: User, **kwargs):
    admin_emails: list[str] = list(
        User.objects.filter(is_superuser=True, is_active=True).values_list('email', flat=True)
    )

    subject = '[xray-genius] New user sign up'
    message = render_to_string(
        template_name='emails/admin_new_user_message.txt',
        context={'user': user},
    )

    EmailMessage(subject=subject, body=message, to=admin_emails).send(fail_silently=False)
