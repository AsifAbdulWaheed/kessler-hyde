from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order, OrderItem
from apps.catalog.models import Product
from apps.shipping.models import SiteSettings


@staff_member_required
def dashboard_home(request):
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()

    status_counts = {
        "pending": Order.objects.filter(order_status=Order.STATUS_PENDING).count(),
        "confirmed": Order.objects.filter(order_status=Order.STATUS_CONFIRMED).count(),
        "processing": Order.objects.filter(order_status=Order.STATUS_PROCESSING).count(),
        "shipped": Order.objects.filter(order_status=Order.STATUS_SHIPPED).count(),
        "delivered": Order.objects.filter(order_status=Order.STATUS_DELIVERED).count(),
        "cancelled": Order.objects.filter(order_status=Order.STATUS_CANCELLED).count(),
    }

    total_sales = Order.objects.exclude(
        order_status=Order.STATUS_CANCELLED
    ).aggregate(total=Sum("grand_total"))["total"] or 0

    best_sellers = (
        OrderItem.objects.exclude(order__order_status=Order.STATUS_CANCELLED)
        .values("product_name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")[:5]
    )

    site_settings = SiteSettings.objects.first()
    low_stock_threshold = site_settings.low_stock_threshold if site_settings else 5
    low_stock_products = Product.objects.filter(
        is_active=True, stock_quantity__lte=low_stock_threshold
    ).order_by("stock_quantity")

    today = timezone.now().date()
    trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_orders = Order.objects.filter(
            created_at__date=day
        ).exclude(order_status=Order.STATUS_CANCELLED)
        day_total = day_orders.aggregate(total=Sum("grand_total"))["total"] or 0
        trend.append({"date": day, "count": day_orders.count(), "total": day_total})

    recent_orders = Order.objects.all()[:10]

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "status_counts": status_counts,
        "total_sales": total_sales,
        "best_sellers": best_sellers,
        "low_stock_products": low_stock_products,
        "low_stock_threshold": low_stock_threshold,
        "trend": trend,
        "recent_orders": recent_orders,
    }
    return render(request, "dashboard/home.html", context)