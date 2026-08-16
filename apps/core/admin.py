from django.contrib import admin
from .models import HomepageContent, Banner


@admin.register(HomepageContent)
class HomepageContentAdmin(admin.ModelAdmin):
    list_display = ["hero_heading", "updated_at"]

    def has_add_permission(self, request):
        return not HomepageContent.objects.exists()


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["order", "is_active", "link"]
    list_filter = ["is_active"]
    ordering = ["order"]