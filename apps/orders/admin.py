from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ["product", "product_name", "color", "size", "quantity", "unit_price", "line_total"]
    readonly_fields = ["product_name", "unit_price", "line_total"]


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    fields = ["old_status", "new_status", "actor_type", "changed_by", "note", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "full_name", "order_status", "grand_total", "created_at"]
    list_filter = ["order_status", "created_at"]
    search_fields = ["order_number", "full_name", "email", "phone"]
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    readonly_fields = ["order_number", "subtotal", "grand_total", "stock_deducted", "created_at", "updated_at"]