from allauth.account.signals import user_signed_up
from django.contrib.auth.models import User
from django.db.models.base import ModelBase
from django.dispatch import receiver

from xray_genius.core.tasks import send_new_user_signup_email_to_admins_task


@receiver(user_signed_up)
def user_signed_up_listener(*, sender: ModelBase, user: User, **kwargs):
    send_new_user_signup_email_to_admins_task.delay(user.pk)
