from django.shortcuts import render, get_object_or_404
from .models import Category, Product


def category_page(request, slug):
    """
    Shows products in a category. Works for both top-level categories
    (e.g. "Men") and child categories (e.g. "Wallets" under "Men").
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)

    # If this is a top-level category, show its own products PLUS
    # products from all its child categories.
    if category.parent is None:
        child_ids = list(category.children.filter(is_active=True).values_list("id", flat=True))
        category_ids = [category.id] + child_ids
    else:
        category_ids = [category.id]

    products = Product.objects.filter(category_id__in=category_ids, is_active=True)

    # Subcategories for the filter chips (only relevant for top-level categories)
    subcategories = category.children.filter(is_active=True) if category.parent is None else []

    context = {
        "category": category,
        "products": products,
        "subcategories": subcategories,
    }
    return render(request, "catalog/category.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    context = {
        "product": product,
    }
    return render(request, "catalog/product_detail.html", context)
def home_page(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:4]
    context = {
        "featured_products": featured_products,
    }
    return render(request, "home.html", context)