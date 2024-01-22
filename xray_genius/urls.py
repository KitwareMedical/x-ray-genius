from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI

from .core import views

api = NinjaAPI(title='X-Ray Genius', version='0.1.0')

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('oauth/', include('oauth2_provider.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/s3-upload/', include('s3_file_field.urls')),
    path('api/v1/', api.urls),
    path('', views.dashboard, name='dashboard'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
