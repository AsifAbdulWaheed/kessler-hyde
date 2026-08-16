from django.contrib import admin
from .models import ReturnRequest


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ["order", "order_item", "request_type", "quantity", "status", "created_at"]
    list_filter = ["status", "request_type", "created_at"]
    search_fields = ["order__order_number"]