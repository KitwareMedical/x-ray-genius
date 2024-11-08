from django import template
from django.template.defaultfilters import stringfilter

from xray_genius.core.models import Session

register = template.Library()


@register.filter
@stringfilter
def status_class(status: str) -> str:
    return {
        Session.Status.NOT_STARTED: 'info',
        Session.Status.QUEUED: 'info',
        Session.Status.RUNNING: 'warning',
        Session.Status.PROCESSED: 'success',
        Session.Status.CANCELLED: 'error',
    }[status]
