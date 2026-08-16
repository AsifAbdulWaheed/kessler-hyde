from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.catalog import views as catalog_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", catalog_views.home_page, name="home"),
    path("", include("apps.catalog.urls")),
]

# Serve uploaded media files during development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)