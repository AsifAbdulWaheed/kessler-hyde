from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.catalog import views as catalog_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", catalog_views.home_page, name="home"),
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    path("returns/", include("apps.returns.urls")),
    path("staff-portal/", include("apps.dashboard.urls")),
    path("", include("apps.core.urls")),
    path("", include("apps.catalog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)