from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.catalog.models import Product
from apps.shipping.models import SiteSettings
from .cart import Cart
from .services import create_order, InsufficientStockError


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", 1))
    color = request.POST.get("color", "")
    size = request.POST.get("size", "")
    cart.add(product_id=product.id, quantity=quantity, color=color, size=size)
    messages.success(request, f"{product.name} added to cart.")
    return redirect("cart:cart_detail")


def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect("cart:cart_detail")


def cart_update(request, product_id):
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    cart.update_quantity(product_id, quantity)
    return redirect("cart:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    subtotal = cart.get_subtotal()

    settings_row = SiteSettings.objects.first()
    if settings_row and subtotal >= settings_row.free_shipping_threshold:
        estimated_shipping = 0
    elif settings_row:
        estimated_shipping = settings_row.flat_shipping_fee
    else:
        estimated_shipping = 0

    context = {
        "cart": cart,
        "subtotal": subtotal,
        "estimated_shipping": estimated_shipping,
        "estimated_total": subtotal + estimated_shipping,
        "free_shipping_threshold": settings_row.free_shipping_threshold if settings_row else None,
    }
    return render(request, "cart/cart_detail.html", context)


def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart_detail")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()
        order_notes = request.POST.get("order_notes", "").strip()

        if not all([full_name, phone, email, address, city, postal_code]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, "cart/checkout.html", {"cart": cart, "subtotal": cart.get_subtotal()})

        customer = request.user if request.user.is_authenticated else None

        try:
            order = create_order(
                cart=cart,
                customer=customer,
                full_name=full_name,
                phone=phone,
                email=email,
                address=address,
                city=city,
                postal_code=postal_code,
                order_notes=order_notes,
            )
        except InsufficientStockError as e:
            messages.error(request, f"Sorry, '{e.product_name}' doesn't have enough stock.")
            return render(request, "cart/checkout.html", {"cart": cart, "subtotal": cart.get_subtotal()})

        cart.clear()
        return redirect("cart:order_confirmation", order_number=order.order_number)

    context = {
        "cart": cart,
        "subtotal": cart.get_subtotal(),
    }
    return render(request, "cart/checkout.html", context)


def order_confirmation(request, order_number):
    from apps.orders.models import Order
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "cart/order_confirmation.html", {"order": order})