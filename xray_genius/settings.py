from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from composed_configuration import (
    ComposedConfiguration,
    ConfigMixin,
    DevelopmentBaseConfiguration,
    HerokuProductionBaseConfiguration,
    ProductionBaseConfiguration,
    TestingBaseConfiguration,
)

if TYPE_CHECKING:
    from django_autotyping.typing import AutotypingSettingsDict


class XrayGeniusMixin(ConfigMixin):
    WSGI_APPLICATION = 'xray_genius.wsgi.application'
    ROOT_URLCONF = 'xray_genius.urls'

    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

    LOGIN_REQUIRED_IGNORE_PATHS = [r'/accounts/']

    ACCOUNT_ADAPTER = 'xray_genius.core.allauth.XrayGeniusAccountAdapter'
    SOCIALACCOUNT_ADAPTER = 'xray_genius.core.allauth.XrayGeniusSocialAccountAdapter'

    @staticmethod
    def mutate_configuration(configuration: ComposedConfiguration) -> None:
        # Install local apps first, to ensure any overridden resources are found first
        configuration.INSTALLED_APPS = [
            'xray_genius.core.apps.CoreConfig',
        ] + configuration.INSTALLED_APPS

        # Install additional apps
        configuration.INSTALLED_APPS += [
            's3_file_field',
            'allauth.socialaccount.providers.google',
            'widget_tweaks',
            'django_vite',
        ]

        # Has to be anywhere after django.contrib.auth.middleware.AuthenticationMiddleware
        configuration.MIDDLEWARE.append('login_required.middleware.LoginRequiredMiddleware')

        # Configure Google OAuth provider
        configuration.SOCIALACCOUNT_PROVIDERS = {
            'google': {
                'APP': {
                    'client_id': os.environ.get('DJANGO_GOOGLE_OAUTH_CLIENT_ID'),
                    'secret': os.environ.get('DJANGO_GOOGLE_OAUTH_SECRET'),
                    'key': '',
                }
            }
        }

        configuration.DJANGO_VITE_MANIFEST_PATH = (
            configuration.BASE_DIR / 'viewer' / 'dist' / 'manifest.json'
        )

        configuration.STATICFILES_DIRS.append(configuration.BASE_DIR / 'viewer' / 'dist')


class DevelopmentConfiguration(XrayGeniusMixin, DevelopmentBaseConfiguration):
    @staticmethod
    def mutate_configuration(configuration: ComposedConfiguration) -> None:
        configuration.INSTALLED_APPS.append('django_autotyping')

        autotyping_config: AutotypingSettingsDict = {
            'STUBS_GENERATION': {
                'LOCAL_STUBS_DIR': Path(configuration.BASE_DIR, 'typings'),
            }
        }
        configuration.AUTOTYPING = autotyping_config


class TestingConfiguration(XrayGeniusMixin, TestingBaseConfiguration):
    pass


class ProductionConfiguration(XrayGeniusMixin, ProductionBaseConfiguration):
    pass


class HerokuProductionConfiguration(XrayGeniusMixin, HerokuProductionBaseConfiguration):
    pass
