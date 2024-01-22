from django.contrib import admin

from xray_genius.core.models import CTInputFile, OutputImage, Session


@admin.register(CTInputFile)
class CTInputFileAdmin(admin.ModelAdmin):
    pass


@admin.register(OutputImage)
class OutputImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass
