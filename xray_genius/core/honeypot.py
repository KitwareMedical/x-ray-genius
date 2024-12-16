import logging

from django.http import HttpRequest
from honeypot.decorators import honeypot_error as base_honeypot_error

logger = logging.getLogger(__name__)


def honeypot_error(request: HttpRequest, context):
    logger.warning('Honeypot error %s, %s', str(request), str(context))
    return base_honeypot_error(request, context)
