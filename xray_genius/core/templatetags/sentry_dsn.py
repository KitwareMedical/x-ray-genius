import os

from django import template

register = template.Library()


@register.simple_tag
def sentry_dsn() -> str | None:
    return os.environ.get('VITE_SENTRY_DSN', None)
