from django.contrib import admin
from .models import PaymentRecord


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ["order", "method", "status", "updated_at"]
    list_filter = ["method", "status"]
    search_fields = ["order__order_number"]