import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import configurations.importer
from django.core.asgi import get_asgi_application
from django.urls import path

from xray_genius.core.notifications import DashboardConsumer

os.environ['DJANGO_SETTINGS_MODULE'] = 'xray_genius.settings'
if not os.environ.get('DJANGO_CONFIGURATION'):
    raise ValueError('The environment variable "DJANGO_CONFIGURATION" must be set.')
configurations.importer.install()

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': AuthMiddlewareStack(
            URLRouter(
                [
                    path('dashboard/', DashboardConsumer.as_asgi(), name='dashboard-ws'),
                ]
            )
        ),
    }
)
