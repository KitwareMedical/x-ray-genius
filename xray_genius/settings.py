from __future__ import annotations

from pathlib import Path

from composed_configuration import (
    ComposedConfiguration,
    ConfigMixin,
    DevelopmentBaseConfiguration,
    HerokuProductionBaseConfiguration,
    ProductionBaseConfiguration,
    TestingBaseConfiguration,
)


class XrayGeniusMixin(ConfigMixin):
    WSGI_APPLICATION = 'xray_genius.wsgi.application'
    ROOT_URLCONF = 'xray_genius.urls'

    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

    @staticmethod
    def mutate_configuration(configuration: ComposedConfiguration) -> None:
        # Install local apps first, to ensure any overridden resources are found first
        configuration.INSTALLED_APPS = [
            'xray_genius.core.apps.CoreConfig',
        ] + configuration.INSTALLED_APPS

        # Install additional apps
        configuration.INSTALLED_APPS += [
            's3_file_field',
        ]


class DevelopmentConfiguration(XrayGeniusMixin, DevelopmentBaseConfiguration):
    pass


class TestingConfiguration(XrayGeniusMixin, TestingBaseConfiguration):
    pass


class ProductionConfiguration(XrayGeniusMixin, ProductionBaseConfiguration):
    pass


class HerokuProductionConfiguration(XrayGeniusMixin, HerokuProductionBaseConfiguration):
    pass
