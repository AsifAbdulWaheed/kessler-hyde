from django.db import models
from django.db.models import Sum


class ReturnRequest(models.Model):
    TYPE_RETURN = "return"
    TYPE_EXCHANGE = "exchange"
    TYPE_CHOICES = [
        (TYPE_RETURN, "Return"),
        (TYPE_EXCHANGE, "Exchange"),
    ]

    STATUS_SUBMITTED = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
    ]

    # Statuses that "lock" their quantity (count against remaining eligible qty)
    ACTIVE_STATUSES = [STATUS_SUBMITTED, STATUS_APPROVED, STATUS_PROCESSING, STATUS_COMPLETED]

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="return_requests")
    order_item = models.ForeignKey("orders.OrderItem", on_delete=models.CASCADE, related_name="return_requests")

    quantity = models.PositiveIntegerField()
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to="returns/", null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_request_type_display()} — {self.order_item.product_name} x{self.quantity}"

    @staticmethod
    def remaining_eligible_quantity(order_item):
        """
        How many units of this order_item can still be requested for
        return/exchange. Rejected requests release their quantity again.
        """
        already_requested = ReturnRequest.objects.filter(
            order_item=order_item,
            status__in=ReturnRequest.ACTIVE_STATUSES,
        ).aggregate(total=Sum("quantity"))["total"] or 0
        return order_item.quantity - already_requested