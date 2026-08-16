from django.db import models


class PaymentRecord(models.Model):
    """
    method = HOW they're paying. status = WHETHER money has moved.
    Keeping these separate avoids confusing "COD" (a method) with a
    payment status.
    """
    METHOD_COD = "cod"
    METHOD_SAFEPAY = "safepay"

    METHOD_CHOICES = [
        (METHOD_COD, "Cash on Delivery"),
        (METHOD_SAFEPAY, "Safepay"),
    ]

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
        (STATUS_REFUNDED, "Refunded"),
    ]

    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="payment_record")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_COD)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    gateway_reference = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.order_number} — {self.get_method_display()} ({self.get_status_display()})"