from django.conf import settings
from django.contrib import admin
from django.urls import include, path
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
    path('session/', views.upload_ct_input_file, name='create-session'),
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
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
