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
from configurations import values

if TYPE_CHECKING:
    from django_autotyping.typing import AutotypingSettingsDict


class XrayGeniusMixin(ConfigMixin):
    WSGI_APPLICATION = 'xray_genius.wsgi.application'
    ROOT_URLCONF = 'xray_genius.urls'

    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

    LOGIN_REQUIRED_IGNORE_PATHS = [r'/accounts/']

    ACCOUNT_ADAPTER = 'xray_genius.core.allauth.XrayGeniusAccountAdapter'
    SOCIALACCOUNT_ADAPTER = 'xray_genius.core.allauth.XrayGeniusSocialAccountAdapter'

    DJANGO_VITE = {
        # Initially empty, to be populated in `mutate_configuration`
        'default': {},
    }

    CELERY_RESULT_BACKEND = 'django-db'
    CELERY_RESULT_EXTENDED = True

    # The maximum number of sessions a user can start
    USER_SESSION_LIMIT = values.IntegerValue(5)

    REQUIRE_APPROVAL_FOR_NEW_USERS = values.BooleanValue(False)

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
            'django_celery_results',
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

        configuration.DJANGO_VITE['default']['manifest_path'] = (
            configuration.BASE_DIR / 'viewer' / 'dist' / 'manifest.json'
        )

        configuration.STATICFILES_DIRS.append(configuration.BASE_DIR / 'viewer' / 'dist')


class DevelopmentConfiguration(XrayGeniusMixin, DevelopmentBaseConfiguration):
    @staticmethod
    def mutate_configuration(configuration: ComposedConfiguration) -> None:
        # Configure django-autotyping in dev-only
        configuration.INSTALLED_APPS.append('django_autotyping')
        autotyping_config: AutotypingSettingsDict = {
            'STUBS_GENERATION': {
                'LOCAL_STUBS_DIR': Path(configuration.BASE_DIR, 'typings'),
            }
        }
        configuration.AUTOTYPING = autotyping_config

        # Configure django-browser-reload in dev-only
        configuration.INSTALLED_APPS.append('django_browser_reload')
        configuration.MIDDLEWARE.append('django_browser_reload.middleware.BrowserReloadMiddleware')

        # Configure django-vite to use the vite dev server in dev environments
        configuration.DJANGO_VITE['default']['dev_mode'] = True
        configuration.DJANGO_VITE['default']['dev_server_port'] = 8080


class TestingConfiguration(XrayGeniusMixin, TestingBaseConfiguration):
    pass


class ProductionConfiguration(XrayGeniusMixin, ProductionBaseConfiguration):
    @staticmethod
    def mutate_configuration(configuration: ComposedConfiguration) -> None:
        configuration.DJANGO_VITE['default']['dev_mode'] = False


class HerokuProductionConfiguration(XrayGeniusMixin, HerokuProductionBaseConfiguration):
    @staticmethod
    def mutate_configuration(configuration: ComposedConfiguration) -> None:
        configuration.DJANGO_VITE['default']['dev_mode'] = False
