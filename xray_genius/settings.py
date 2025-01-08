from __future__ import annotations

from datetime import timedelta
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
import dj_database_url

if TYPE_CHECKING:
    from django_autotyping.typing import AutotypingSettingsDict


class XrayGeniusMixin(ConfigMixin):
    ASGI_APPLICATION = 'xray_genius.asgi.application'
    WSGI_APPLICATION = 'xray_genius.wsgi.application'
    ROOT_URLCONF = 'xray_genius.urls'

    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

    LOGIN_REQUIRED_IGNORE_PATHS = [r'/accounts/', r'/captcha/']

    ACCOUNT_ADAPTER = 'xray_genius.core.allauth.XrayGeniusAccountAdapter'
    SOCIALACCOUNT_ADAPTER = 'xray_genius.core.allauth.XrayGeniusSocialAccountAdapter'

    # Disabling this causes the user to be redirected to the socialaccount signup form, which
    # we need to do to show the TOS checkbox
    SOCIALACCOUNT_AUTO_SIGNUP = False

    # Use custom signup forms to show the TOS checkbox
    ACCOUNT_FORMS = {'signup': 'xray_genius.core.allauth.XrayGeniusAccountSignupForm'}
    SOCIALACCOUNT_FORMS = {'signup': 'xray_genius.core.allauth.XrayGeniusSocialAccountSignupForm'}

    DJANGO_VITE = {
        # Initially empty, to be populated in `mutate_configuration`
        'default': {},
    }

    CELERY_RESULT_BACKEND = 'django-db'
    CELERY_RESULT_EXTENDED = True

    # TODO: remove once this is resolved upstream
    # https://github.com/kitware-resonant/django-composed-configuration/pull/215
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

    CHANNEL_LAYERS = {
        'default': {
            # TODO: switch to channels_redis.pubsub.RedisPubSubChannelLayer when it's out of beta
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                # Use db 1 for channels backend, as 0 is used by celery
                'hosts': [
                    {
                        'address': os.environ['REDIS_URL'],
                        'db': 1,
                    }
                ],
            },
        },
    }

    # The maximum number of failed login attempts before a user is locked out
    AXES_FAILURE_LIMIT = 10

    # The maximum number of sessions a user can start
    USER_SESSION_LIMIT = values.IntegerValue(5)

    # The number of seconds after which a session is considered "stuck".
    # A beat task will check for stuck sessions and send a Sentry alert if any are found.
    SESSION_TIMEOUT = values.IntegerValue(timedelta(minutes=5).total_seconds())

    REQUIRE_APPROVAL_FOR_NEW_USERS = values.BooleanValue(default=True)
    ADDITIONAL_ADMIN_EMAILS = values.ListValue()

    @staticmethod
    def mutate_configuration(configuration: ComposedConfiguration) -> None:
        # Install local apps first, to ensure any overridden resources are found first
        configuration.INSTALLED_APPS = [
            'daphne',
            'xray_genius.core.apps.CoreConfig',
            *configuration.INSTALLED_APPS,
        ]

        # allauth-ui replaces django-auth-style
        configuration.INSTALLED_APPS[configuration.INSTALLED_APPS.index('auth_style')] = (
            'allauth_ui'
        )

        # Install additional apps
        configuration.INSTALLED_APPS += [
            's3_file_field',
            'allauth.socialaccount.providers.google',
            'widget_tweaks',  # required by django-allauth-ui
            'slippers',  # required by django-allauth-ui
            'django_vite',
            'django_celery_results',
            'captcha',
            'axes',
        ]

        # Has to be anywhere after django.contrib.auth.middleware.AuthenticationMiddleware
        configuration.MIDDLEWARE.append('login_required.middleware.LoginRequiredMiddleware')

        configuration.MIDDLEWARE.append('axes.middleware.AxesMiddleware')

        # Has to come first in AUTHENTICATION_BACKENDS
        configuration.AUTHENTICATION_BACKENDS = [
            'axes.backends.AxesStandaloneBackend',
            *configuration.AUTHENTICATION_BACKENDS,
        ]

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

        configuration.CELERY_BEAT_SCHEDULE = {
            'detect-stuck-sessions': {
                'task': 'xray_genius.core.tasks.check_for_stuck_sessions_beat',
                'schedule': timedelta(minutes=1).total_seconds(),
            }
        }


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
    # Heroku's uses a reverse proxy, so we need to use the X-FORWARDED-FOR header
    # to get the real IP address of the client
    AXES_IPWARE_META_PRECEDENCE_ORDER = [
        'HTTP_X_FORWARDED_FOR',
        'REMOTE_ADDR',
    ]

    @staticmethod
    def mutate_configuration(configuration: ComposedConfiguration) -> None:
        configuration.DJANGO_VITE['default']['dev_mode'] = False

        # Redis providers on Heroku use self-signed certs, so we need to disable verification
        configuration.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]['ssl_cert_reqs'] = None

        # We're configuring sentry by hand since we need to pass custom options (sentry cron).
        configuration.INSTALLED_APPS.remove('composed_configuration.sentry.apps.SentryConfig')

    @property
    def CELERY_BROKER_URL(self) -> str:  # noqa: N802
        # Redis providers on Heroku use self-signed certs, so we need to disable verification
        return f'{os.environ["REDIS_URL"]}/0?ssl_cert_reqs=none'

    @property
    def DATABASES(self):  # noqa: N802
        return {
            'default': {
                **dj_database_url.parse(os.environ['DATABASE_URL']),
                'OPTIONS': {
                    'pool': {
                        # We have 20 available postgres connections on our service tier, and some
                        # will be required by the workers and maybe other miscellaneous access.
                        'max_size': 12,
                    },
                },
            },
        }
