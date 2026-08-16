from django.db import models
from django.contrib.auth.models import User
from apps.catalog.models import Product


class Order(models.Model):
    """
    Stores a shipping/contact SNAPSHOT directly on the order —
    this data must never change even if the customer later edits
    their saved account address.
    """
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    order_number = models.CharField(max_length=30, unique=True, db_index=True)

    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )  # null = guest order

    # ---- Shipping/contact SNAPSHOT (authoritative for this order) ----
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(db_index=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    # Optional convenience-only pointer back to a saved Address —
    # NEVER used to render the order, only for admin cross-reference.
    saved_address_ref = models.ForeignKey(
        "accounts.Address",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders_used_in",
    )

    order_notes = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)

    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Prevents double stock deduction/restoration — see architecture notes.
    stock_deducted = models.BooleanField(default=False)

    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """
    Stores a full SNAPSHOT of what was actually purchased. `product`
    stays nullable so old orders survive even if the product is
    later deleted — but the product FK is for admin reference only,
    never for rendering the order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )

    # ---- Snapshot fields (authoritative for this order item) ----
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity} — {self.order.order_number}"


class OrderStatusHistory(models.Model):
    """
    Every status transition is recorded here. Order.order_status must
    NEVER be updated directly by application code — always go through
    one service function that updates the field AND writes this row
    in the same transaction.
    """
    ACTOR_ADMIN = "admin"
    ACTOR_STAFF = "staff"
    ACTOR_CUSTOMER = "customer"
    ACTOR_SYSTEM = "system"

    ACTOR_CHOICES = [
        (ACTOR_ADMIN, "Admin"),
        (ACTOR_STAFF, "Staff"),
        (ACTOR_CUSTOMER, "Customer"),
        (ACTOR_SYSTEM, "System"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    actor_type = models.CharField(max_length=20, choices=ACTOR_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Order status histories"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.order.order_number}: {self.old_status} → {self.new_status}"