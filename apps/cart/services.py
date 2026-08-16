import random
import string
from decimal import Decimal
from django.db import transaction
from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.payments.models import PaymentRecord
from apps.shipping.models import SiteSettings


class InsufficientStockError(Exception):
    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(f"Not enough stock for {product_name}")


def generate_order_number():
    from django.utils import timezone
    date_part = timezone.now().strftime("%Y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"KH-{date_part}-{random_part}"


@transaction.atomic
def create_order(cart, customer, full_name, phone, email, address, city, postal_code, order_notes=""):
    """
    Server-authoritative order creation.
    - Re-checks stock and price for every item from the database.
    - Deducts stock atomically, with row locking to prevent race conditions.
    - Never trusts any price/quantity value from the cart's cached session data
      beyond WHICH product and HOW MANY — price is always recalculated here.
    """
    site_settings = SiteSettings.objects.first()

    # Step 1: Check stock for every item first (fail fast, before touching anything)
    locked_products = {}
    for item in cart:
        product = Product.objects.select_for_update().get(id=item["product"].id)
        if product.stock_quantity < item["quantity"]:
            raise InsufficientStockError(product.name)
        locked_products[product.id] = product

    # Step 2: Calculate subtotal server-side using CURRENT prices
    subtotal = Decimal("0.00")
    line_items = []
    for item in cart:
        product = locked_products[item["product"].id]
        charged_price = product.get_charged_price()  # sale-aware
        line_total = charged_price * item["quantity"]
        subtotal += line_total
        line_items.append({
            "product": product,
            "quantity": item["quantity"],
            "color": item["color"],
            "size": item["size"],
            "unit_price": charged_price,
            "line_total": line_total,
        })

    # Step 3: Calculate shipping server-side
    if site_settings and subtotal >= site_settings.free_shipping_threshold:
        delivery_charge = Decimal("0.00")
    elif site_settings:
        delivery_charge = site_settings.flat_shipping_fee
    else:
        delivery_charge = Decimal("0.00")

    grand_total = subtotal + delivery_charge

    # Step 4: Create the Order with a unique order_number
    order_number = generate_order_number()
    while Order.objects.filter(order_number=order_number).exists():
        order_number = generate_order_number()

    order = Order.objects.create(
        order_number=order_number,
        customer=customer,
        full_name=full_name,
        phone=phone,
        email=email,
        address=address,
        city=city,
        postal_code=postal_code,
        order_notes=order_notes,
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        grand_total=grand_total,
        order_status=Order.STATUS_PENDING,
        stock_deducted=False,
    )

    # Step 5: Create OrderItems + deduct stock (all within this same atomic block)
    for line in line_items:
        product = line["product"]
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            unit_price=line["unit_price"],
            color=line["color"],
            size=line["size"],
            quantity=line["quantity"],
            line_total=line["line_total"],
        )
        product.stock_quantity -= line["quantity"]
        if product.stock_quantity == 0:
            product.is_active = False
        product.save()

    order.stock_deducted = True
    order.save()

    # Step 6: Record initial status history
    OrderStatusHistory.objects.create(
        order=order,
        old_status="",
        new_status=Order.STATUS_PENDING,
        changed_by=customer,
        actor_type=OrderStatusHistory.ACTOR_CUSTOMER if customer else OrderStatusHistory.ACTOR_SYSTEM,
        note="Order placed.",
    )

    # Step 7: Create PaymentRecord (COD only, at launch)
    PaymentRecord.objects.create(
        order=order,
        method=PaymentRecord.METHOD_COD,
        status=PaymentRecord.STATUS_PENDING,
    )

    return order