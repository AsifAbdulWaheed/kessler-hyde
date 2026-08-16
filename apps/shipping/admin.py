from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["flat_shipping_fee", "free_shipping_threshold", "delivery_min_days", "delivery_max_days", "low_stock_threshold", "return_window_days"]

    def has_add_permission(self, request):
        # Only allow adding if no SiteSettings row exists yet
        return not SiteSettings.objects.exists()