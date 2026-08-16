from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order
from .services import cancel_order, CancellationNotAllowedError, OrderStatusHistory


def track_order(request):
    order = None
    if request.method == "POST":
        order_number = request.POST.get("order_number", "").strip()
        contact = request.POST.get("contact", "").strip()

        order = Order.objects.filter(order_number=order_number).filter(
            models_q_email_or_phone(contact)
        ).first()

        if not order:
            messages.error(request, "No order found with that Order Number and Email/Phone combination.")

    return render(request, "orders/track_order.html", {"order": order})


def models_q_email_or_phone(contact):
    from django.db.models import Q
    return Q(email__iexact=contact) | Q(phone=contact)


def cancel_order_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == "POST":
        try:
            cancel_order(
                order,
                changed_by=request.user if request.user.is_authenticated else None,
                actor_type=OrderStatusHistory.ACTOR_CUSTOMER,
                note="Self-cancelled by customer.",
            )
            messages.success(request, f"Order {order.order_number} has been cancelled.")
        except CancellationNotAllowedError:
            messages.error(request, "This order can no longer be cancelled. Please contact support.")

    return redirect("orders:track_order")


def my_orders(request):
    if not request.user.is_authenticated:
        return redirect("orders:track_order")
    orders = Order.objects.filter(customer=request.user)
    return render(request, "orders/my_orders.html", {"orders": orders})