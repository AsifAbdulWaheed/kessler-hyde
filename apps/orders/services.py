from django.db import transaction
from django.utils import timezone
from .models import Order, OrderStatusHistory
from apps.catalog.models import Product


class CancellationNotAllowedError(Exception):
    pass


@transaction.atomic
def update_order_status(order, new_status, changed_by=None, actor_type=OrderStatusHistory.ACTOR_ADMIN, note=""):
    """
    THE ONLY function allowed to change Order.order_status.
    Updates the status AND writes the history row in the same transaction,
    so they can never drift out of sync.
    """
    order = Order.objects.select_for_update().get(id=order.id)
    old_status = order.order_status
    order.order_status = new_status
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        actor_type=actor_type,
        note=note,
    )
    return order


@transaction.atomic
def cancel_order(order, changed_by=None, actor_type=OrderStatusHistory.ACTOR_CUSTOMER, note="Cancelled by customer."):
    """
    Cancels a Pending order: restores stock (only if it was deducted
    and hasn't been restored already — the stock_deducted flag
    prevents double-restoration), then updates status.
    """
    order = Order.objects.select_for_update().get(id=order.id)

    if order.order_status != Order.STATUS_PENDING:
        raise CancellationNotAllowedError("Only Pending orders can be self-cancelled.")

    if order.stock_deducted:
        for item in order.items.all():
            if item.product:
                product = Product.objects.select_for_update().get(id=item.product.id)
                product.stock_quantity += item.quantity
                product.is_active = True
                product.save()
        order.stock_deducted = False

    order.cancelled_at = timezone.now()
    order.save()

    update_order_status(order, Order.STATUS_CANCELLED, changed_by=changed_by, actor_type=actor_type, note=note)
    return order