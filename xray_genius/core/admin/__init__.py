import csv
from datetime import datetime, timedelta

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Max, QuerySet
from django.http import StreamingHttpResponse
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

admin.site.site_header = 'X-ray Genius Admin'
admin.site.site_title = 'X-ray Genius Admin'

# Unregister the default User model so we can register our own
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_active')

    actions = ['approve_users', 'unapprove_users', 'export_users_to_csv']

    @admin.action(description='Approve selected users')
    def approve_users(self, request, queryset: QuerySet[User]) -> None:
        queryset.update(is_active=True)

    @admin.action(description='Unapprove selected users')
    def unapprove_users(self, request, queryset: QuerySet[User]) -> None:
        queryset.update(is_active=False)

    @admin.action(description='Export selected users to CSV')
    def export_users_to_csv(self, request, queryset: QuerySet[User]) -> StreamingHttpResponse:
        # https://docs.djangoproject.com/en/5.1/howto/outputting-csv/#streaming-large-csv-files
        pseudo_buffer = self._Echo()
        writer = csv.writer(pseudo_buffer)
        rows = User.objects.values_list('email', 'first_name', 'last_name', 'is_active')
        return StreamingHttpResponse(
            streaming_content=(writer.writerow(row) for row in rows),
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="users.csv"'},
        )

    class _Echo:
        def write(self, value):
            return value


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
        if most_recent_image_created and obj.started:
            duration: timedelta = most_recent_image_created - obj.started
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
