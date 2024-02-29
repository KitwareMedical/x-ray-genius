from django.contrib import admin

from xray_genius.core.models import CTInputFile, OutputImage, Session

admin.site.site_header = 'X-Ray Genius Admin'
admin.site.site_title = 'X-Ray Genius Admin'


@admin.register(CTInputFile)
class CTInputFileAdmin(admin.ModelAdmin):
    pass


@admin.register(OutputImage)
class OutputImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('created', 'owner', 'status')
