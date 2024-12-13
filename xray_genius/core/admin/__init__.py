from django.contrib import admin

from xray_genius.core.models import (
    ContactFormSubmission,
    CTInputFile,
    InputParameters,
    OutputImage,
    SampleDataset,
    SampleDatasetFile,
    Session,
)

admin.site.site_header = 'X-Ray Genius Admin'
admin.site.site_title = 'X-Ray Genius Admin'


@admin.register(CTInputFile)
class CTInputFileAdmin(admin.ModelAdmin):
    pass


@admin.register(OutputImage)
class OutputImageAdmin(admin.ModelAdmin):
    pass


class SessionInputParametersInline(admin.StackedInline):
    model = InputParameters


class SessionOutputImageInline(admin.TabularInline):
    model = OutputImage


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('created', 'owner', 'status')
    inlines = (
        SessionInputParametersInline,
        SessionOutputImageInline,
    )


class SampleDatasetFileInline(admin.TabularInline):
    model = SampleDatasetFile


@admin.register(SampleDataset)
class SampleDatasetAdmin(admin.ModelAdmin):
    inlines = (SampleDatasetFileInline,)


@admin.register(ContactFormSubmission)
class ContactFormSubmissionAdmin(admin.ModelAdmin):
    pass
