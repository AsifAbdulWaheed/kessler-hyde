from django.contrib import admin
from .models import Address, WishlistItem


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["full_name", "customer", "city", "phone"]
    search_fields = ["full_name", "phone", "email"]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ["customer", "product", "added_at"]
    list_filter = ["added_at"]