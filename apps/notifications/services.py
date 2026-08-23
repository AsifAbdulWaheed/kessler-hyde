"""
Central email service for Kessler & Hyde.
All 7 email types go through send_order_email().
Fails gracefully — a failed email never breaks the order flow.
Dev: prints to console (EMAIL_BACKEND = console)
Prod: sends via Brevo SMTP
"""
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

# Event type constants
ORDER_PLACED = "order_placed"
ORDER_CONFIRMED = "order_confirmed"
ORDER_SHIPPED = "order_shipped"
ORDER_DELIVERED = "order_delivered"
ORDER_CANCELLED = "order_cancelled"
RETURN_UPDATE = "return_update"
ADMIN_NEW_ORDER = "admin_new_order"

EMAIL_SUBJECTS = {
    ORDER_PLACED: "Order Confirmed — {order_number}",
    ORDER_CONFIRMED: "Your Order Has Been Confirmed — {order_number}",
    ORDER_SHIPPED: "Your Order Is On Its Way — {order_number}",
    ORDER_DELIVERED: "Your Order Has Been Delivered — {order_number}",
    ORDER_CANCELLED: "Your Order Has Been Cancelled — {order_number}",
    RETURN_UPDATE: "Return/Exchange Update — {order_number}",
    ADMIN_NEW_ORDER: "New Order Received — {order_number}",
}

TEMPLATE_MAP = {
    ORDER_PLACED: "notifications/order_placed.html",
    ORDER_CONFIRMED: "notifications/order_confirmed.html",
    ORDER_SHIPPED: "notifications/order_shipped.html",
    ORDER_DELIVERED: "notifications/order_delivered.html",
    ORDER_CANCELLED: "notifications/order_cancelled.html",
    RETURN_UPDATE: "notifications/return_update.html",
    ADMIN_NEW_ORDER: "notifications/admin_new_order.html",
}


def send_order_email(event_type, order, extra_context=None):
    """
    Send a branded email for the given event_type.
    Never raises — logs errors instead so order flow is never broken.
    """
    try:
        subject = EMAIL_SUBJECTS[event_type].format(order_number=order.order_number)
        template = TEMPLATE_MAP[event_type]

        context = {"order": order}
        if extra_context:
            context.update(extra_context)

        html_message = render_to_string(template, context)
        plain_message = f"Order {order.order_number} — visit our website for full details."

        if event_type == ADMIN_NEW_ORDER:
            recipient = settings.DEFAULT_FROM_EMAIL
        else:
            recipient = order.email

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent: {event_type} for {order.order_number}")

    except Exception as e:
        logger.error(f"Email failed: {event_type} for order {getattr(order, 'order_number', '?')} — {e}")