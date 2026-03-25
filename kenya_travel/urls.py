from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import health_check


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path("health/", health_check, name="health"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


