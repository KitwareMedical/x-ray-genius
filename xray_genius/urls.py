from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from ninja import NinjaAPI

from .core import views
from .core.rest.session import session_router

api = NinjaAPI(title='X-Ray Genius', version='0.1.0')
api.add_router('/session/', session_router)

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('oauth/', include('oauth2_provider.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/s3-upload/', include('s3_file_field.urls')),
    path('api/v1/', api.urls),
    path('', views.dashboard, name='dashboard'),
    path('contact/', views.contact_form, name='contact'),
    path('session/', views.upload_ct_input_file, name='create-session'),
    path(
        'session/from-sample-data/<int:sample_dataset_file_pk>/',
        views.start_session_with_sample_data,
        name='create-session-from-sample-data',
    ),
    path('session/<uuid:session_pk>/delete/', views.delete_session, name='delete-session'),
    path(
        'session/<uuid:session_pk>/input-ct-file/',
        views.download_ct_file,
        name='download-input-ct-file',
    ),
    path(
        'session/<uuid:session_pk>/viewer/',
        views.volview_viewer,
        name='viewer',
    ),
    path(
        'session/<uuid:session_pk>/initiate-batch-run/',
        views.initiate_batch_run,
        name='initiate-batch-run',
    ),
    path(
        'session/<uuid:session_pk>/cancel-batch-run/',
        views.cancel_batch_run,
        name='cancel-batch-run',
    ),
    path(
        'session/<uuid:session_pk>/trace/',
        views.get_task_trace,
        name='get-task-trace',
    ),
    # TODO: these are hardcoded because the frontend refers to them directly as absolute URLs
    path(
        'itk/<path:path>',
        RedirectView.as_view(url='/static/itk/%(path)s', permanent=True),
        name='itk',
    ),
]

if settings.DEBUG:
    import debug_toolbar
    import django_browser_reload.urls

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('__reload__/', include(django_browser_reload.urls)),
        *urlpatterns,
    ]
