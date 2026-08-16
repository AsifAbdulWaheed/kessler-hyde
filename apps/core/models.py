from django.db import models
from django.core.exceptions import ValidationError


class HomepageContent(models.Model):
    """
    Singleton model — only one row should ever exist. Lets the admin
    edit the homepage without touching code.
    """
    hero_heading = models.CharField(max_length=200, default="Kessler & Hyde")
    hero_description = models.TextField(
        default="Timeless Leather, Made to Last."
    )
    hero_image = models.ImageField(upload_to="homepage/", null=True, blank=True)
    hero_cta_text = models.CharField(max_length=50, default="Shop Now")
    hero_cta_link = models.CharField(max_length=200, default="/")

    announcement_text = models.CharField(max_length=255, blank=True)
    leather_quality_section = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Homepage Content"

    def __str__(self):
        return "Homepage Content"

    def clean(self):
        if not self.pk and HomepageContent.objects.exists():
            raise ValidationError("Homepage Content already exists — edit the existing row instead of creating a new one.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Banner(models.Model):
    image = models.ImageField(upload_to="banners/")
    link = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Banner {self.order}"