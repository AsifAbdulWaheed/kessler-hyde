from django.contrib import admin
from .models import Category, Product, ProductImage, ProductColor


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "is_primary", "order"]


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    fields = ["color_name", "color_hex"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "is_active"]
    list_filter = ["is_active", "parent"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "regular_price", "sale_price", "is_on_sale", "stock_quantity", "is_active", "is_featured"]
    list_filter = ["category", "is_active", "is_featured", "is_on_sale"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductColorInline]