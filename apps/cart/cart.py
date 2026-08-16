from decimal import Decimal
from apps.catalog.models import Product


class Cart:
    """
    Session-based shopping cart. Works for both guests and logged-in
    customers (session persists either way).

    IMPORTANT: All totals shown here are DISPLAY-ONLY ESTIMATES.
    The server recalculates everything from scratch at checkout —
    nothing stored in the cart/session is trusted for the final order.
    """
    SESSION_KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if cart is None:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def add(self, product_id, quantity=1, color="", size=""):
        key = str(product_id)
        if key in self.cart:
            self.cart[key]["quantity"] += quantity
        else:
            self.cart[key] = {"quantity": quantity, "color": color, "size": size}
        self.save()

    def update_quantity(self, product_id, quantity):
        key = str(product_id)
        if key in self.cart:
            if quantity <= 0:
                del self.cart[key]
            else:
                self.cart[key]["quantity"] = quantity
            self.save()

    def remove(self, product_id):
        key = str(product_id)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        """
        Yields display-only line items by re-reading current product
        data from the database each time — never trusts stale session data.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}

        for product_id, item in self.cart.items():
            product = products_map.get(product_id)
            if not product:
                continue  # product was deleted — skip silently
            charged_price = product.get_charged_price()
            yield {
                "product": product,
                "quantity": item["quantity"],
                "color": item.get("color", ""),
                "size": item.get("size", ""),
                "unit_price": charged_price,
                "line_total": charged_price * item["quantity"],
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_subtotal(self):
        return sum((line["line_total"] for line in self), Decimal("0.00"))