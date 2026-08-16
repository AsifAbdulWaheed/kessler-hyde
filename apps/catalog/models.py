from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
    """
    Product categories. Supports ONE level of parent/child nesting only
    (e.g. Men -> Wallets). A category with no parent is top-level.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def clean(self):
        # Enforce only ONE level of nesting: a category's parent
        # cannot itself already have a parent.
        if self.parent and self.parent.parent:
            raise ValidationError(
                "Only one level of category nesting is allowed. "
                f"'{self.parent}' already has a parent category."
            )


class Product(models.Model):
    """
    A single product. Stock is tracked as one simple number at launch
    (Product.stock_quantity). Colors are display-only tags for now —
    see ProductColor below.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # can't delete a category while products use it
        related_name="products",
    )

    leather_type = models.CharField(
        max_length=150,
        default="Leather type — to be specified",
        blank=True,
    )

    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_on_sale = models.BooleanField(default=False)

    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)  # "Best Leather Products"

    # Mainly used for Bags — optional for other product types
    size_label = models.CharField(max_length=50, blank=True)
    size_dimensions = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
           models.CheckConstraint(
                condition=models.Q(stock_quantity__gte=0),
                name="catalog_product_stock_never_negative",
            )
        ]

    def __str__(self):
        return self.name

    def get_charged_price(self):
        """
        Returns the price that should actually be charged right now.
        Used by checkout — never trust a price from the browser.
        """
        if self.is_on_sale and self.sale_price is not None:
            return self.sale_price
        return self.regular_price


class ProductImage(models.Model):
    """
    2-4 images per product. Exactly one should be marked primary —
    enforced in save() below, not just by admin discipline.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name} — image {self.order}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_primary:
            # Unset is_primary on every other image of this product
            ProductImage.objects.filter(product=self.product).exclude(pk=self.pk).update(is_primary=False)


class ProductColor(models.Model):
    """
    Lightweight color tag per product. No stock of its own at launch —
    see the architecture notes on ProductVariant for the future extension.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors")
    color_name = models.CharField(max_length=50)
    color_hex = models.CharField(max_length=7, blank=True, help_text="e.g. #3C2A21")

    def __str__(self):
        return f"{self.product.name} — {self.color_name}"