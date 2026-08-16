from django.db import models
from django.contrib.auth.models import User
from apps.catalog.models import Product


class Address(models.Model):
    """
    A customer's saved address (for registered accounts only).
    NOTE: Orders do NOT read from this model directly — orders store
    their own address snapshot. This model is only for the
    "save my address for next time" convenience feature.
    """
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.full_name} — {self.city}"


class WishlistItem(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customer", "product")  # can't wishlist the same product twice

    def __str__(self):
        return f"{self.customer.username} — {self.product.name}"
