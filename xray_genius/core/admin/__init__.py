from datetime import datetime, timedelta

from django.contrib import admin
from django.db.models import Max
import humanize

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
    list_display = ('created', 'owner', 'status', 'get_duration')
    inlines = (
        SessionInputParametersInline,
        SessionOutputImageInline,
    )

    def get_queryset(self, request):
        # Prefetch the maximum created timestamp from related output_images
        # so we have it for the get_duration method
        qs = super().get_queryset(request)
        return qs.annotate(latest_image_created=Max('output_images__created'))

    @admin.display(description='Duration')
    def get_duration(self, obj: Session) -> str:
        # The duration of the Session can be calculated as the difference between the
        # most recent OutputImage and the Session's creation time.
        most_recent_image_created: datetime | None = getattr(obj, 'latest_image_created', None)
        if most_recent_image_created:
            duration: timedelta = most_recent_image_created - obj.created
            return humanize.precisedelta(duration)
        return 'N/A'


class SampleDatasetFileInline(admin.TabularInline):
    model = SampleDatasetFile


@admin.register(SampleDataset)
class SampleDatasetAdmin(admin.ModelAdmin):
    inlines = (SampleDatasetFileInline,)


@admin.register(ContactFormSubmission)
class ContactFormSubmissionAdmin(admin.ModelAdmin):
    pass
