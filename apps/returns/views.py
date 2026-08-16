from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order, OrderItem
from apps.shipping.models import SiteSettings
from .models import ReturnRequest


def returns_lookup(request):
    order = None
    if request.method == "POST":
        order_number = request.POST.get("order_number", "").strip()
        contact = request.POST.get("contact", "").strip()

        order = Order.objects.filter(order_number=order_number).filter(
            Q(email__iexact=contact) | Q(phone=contact)
        ).first()

        if not order:
            messages.error(request, "No order found with that Order Number and Email/Phone combination.")
        elif order.order_status != Order.STATUS_DELIVERED:
            messages.error(request, "Returns can only be requested for delivered orders.")
            order = None

    site_settings = SiteSettings.objects.first()
    return_window_days = site_settings.return_window_days if site_settings else 14

    items_with_eligibility = []
    if order:
        for item in order.items.all():
            remaining = ReturnRequest.remaining_eligible_quantity(item)
            items_with_eligibility.append({"item": item, "remaining": remaining})

    context = {
        "order": order,
        "items_with_eligibility": items_with_eligibility,
        "return_window_days": return_window_days,
    }
    return render(request, "returns/returns_lookup.html", context)


def submit_return(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = order_item.order

    site_settings = SiteSettings.objects.first()
    return_window_days = site_settings.return_window_days if site_settings else 14
    remaining = ReturnRequest.remaining_eligible_quantity(order_item)

    if order.order_status != Order.STATUS_DELIVERED:
        messages.error(request, "This order is not eligible for returns.")
        return redirect("returns:returns_lookup")

    if remaining <= 0:
        messages.error(request, "No remaining eligible quantity for this item.")
        return redirect("returns:returns_lookup")

    if request.method == "POST":
        request_type = request.POST.get("request_type")
        quantity = int(request.POST.get("quantity", 1))
        reason = request.POST.get("reason", "").strip()
        notes = request.POST.get("notes", "").strip()
        photo = request.FILES.get("photo")

        if quantity > remaining:
            messages.error(request, f"You can only request up to {remaining} unit(s) for this item.")
        elif not reason:
            messages.error(request, "Please provide a reason.")
        else:
            ReturnRequest.objects.create(
                order=order,
                order_item=order_item,
                quantity=quantity,
                request_type=request_type,
                reason=reason,
                notes=notes,
                photo=photo,
            )
            messages.success(request, "Your request has been submitted. We'll review it shortly.")
            return redirect("returns:returns_lookup")

    context = {
        "order_item": order_item,
        "remaining": remaining,
    }
    return render(request, "returns/submit_return.html", context)