from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'xray_genius.core'
    verbose_name = 'xray_genius: Core'

    def ready(self):
        import xray_genius.core.signals  # noqa: F401

        return super().ready()
