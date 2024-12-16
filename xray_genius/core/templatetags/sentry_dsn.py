from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def sentry_dsn() -> str | None:
    return getattr(settings, 'SENTRY_DSN', None)
