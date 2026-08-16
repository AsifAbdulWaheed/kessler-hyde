from django.db import models
from django.core.exceptions import ValidationError


class SiteSettings(models.Model):
    """
    Single store-wide settings row (singleton pattern — only one row
    should ever exist). Admin edits these values; code never
    hardcodes shipping fees, thresholds, or estimates.
    """
    flat_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)

    delivery_min_days = models.PositiveIntegerField(default=3)
    delivery_max_days = models.PositiveIntegerField(default=5)

    low_stock_threshold = models.PositiveIntegerField(default=5)
    return_window_days = models.PositiveIntegerField(default=14)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    def clean(self):
        # Enforce singleton: only one SiteSettings row should exist
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("Site Settings already exists — edit the existing row instead of creating a new one.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)