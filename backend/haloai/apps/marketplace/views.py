from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from .models import Category, Product, Vendor, Order, OrderItem
from apps.users.models import FarmerProfile


@login_required
def marketplace_home(request):
    """Main marketplace page for farmers"""
    if not request.user.is_farmer:
        messages.error(request, "Access denied. This page is for farmers only.")
        return redirect("dashboard:redirect")

    # Get farmer's region for regional products
    try:
        farmer_profile = FarmerProfile.objects.get(user=request.user)
        region = farmer_profile.farm_location
    except FarmerProfile.DoesNotExist:
        region = "Bhairahawa-Butwal"

    # Featured products
    featured_products = Product.objects.filter(
        is_featured=True,
        is_available=True,
        vendor__region__icontains=region.split(",")[0] if "," in region else region,
    )[:6]

    # Categories
    categories = Category.objects.filter(is_active=True)

    # Recent orders
    recent_orders = Order.objects.filter(farmer=request.user).order_by("-created_at")[
        :3
    ]

    context = {
        "featured_products": featured_products,
        "categories": categories,
        "recent_orders": recent_orders,
        "farmer_region": region,
    }

    return render(request, "marketplace/home.html", context)


@login_required
def product_list(request):
    """Product listing with filters"""
    if not request.user.is_farmer:
        return redirect("dashboard:redirect")

    products = Product.objects.filter(is_available=True)

    # Filters
    category_id = request.GET.get("category")
    product_type = request.GET.get("type")
    search_query = request.GET.get("q")
    price_range = request.GET.get("price_range")

    if category_id:
        products = products.filter(category_id=category_id)

    if product_type:
        products = products.filter(product_type=product_type)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    if price_range:
        if price_range == "low":
            products = products.filter(price__lt=1000)
        elif price_range == "medium":
            products = products.filter(price__gte=1000, price__lt=5000)
        elif price_range == "high":
            products = products.filter(price__gte=5000)

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)

    context = {
        "products": products_page,
        "categories": Category.objects.filter(is_active=True),
        "current_filters": {
            "category": category_id,
            "type": product_type,
            "search": search_query,
            "price_range": price_range,
        },
    }

    return render(request, "marketplace/product_list.html", context)


@login_required
def product_detail(request, product_id):
    """Individual product detail page"""
    if not request.user.is_farmer:
        return redirect("dashboard:redirect")

    product = get_object_or_404(Product, id=product_id, is_available=True)
    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(id=product.id)[:4]

    context = {
        "product": product,
        "related_products": related_products,
    }

    return render(request, "marketplace/product_detail.html", context)


@login_required
def add_to_cart(request):
    """AJAX endpoint to add products to cart (session-based)"""
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id)

        # Get or create cart in session
        cart = request.session.get("cart", {})

        if product_id in cart:
            cart[product_id]["quantity"] += quantity
        else:
            cart[product_id] = {
                "quantity": quantity,
                "price": float(product.price),
                "name": product.name,
                "unit": product.unit,
            }

        request.session["cart"] = cart
        request.session.modified = True

        return JsonResponse(
            {
                "success": True,
                "message": f"{product.name} added to cart",
                "cart_count": sum(item["quantity"] for item in cart.values()),
            }
        )

    return JsonResponse({"success": False})


@login_required
def cart_view(request):
    """Shopping cart page"""
    if not request.user.is_farmer:
        return redirect("dashboard:redirect")

    cart = request.session.get("cart", {})
    cart_items = []
    total_amount = 0

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = item["quantity"] * item["price"]
        total_amount += item_total

        cart_items.append(
            {
                "product": product,
                "quantity": item["quantity"],
                "price": item["price"],
                "total": item_total,
            }
        )

    context = {
        "cart_items": cart_items,
        "total_amount": total_amount,
        "commission_amount": total_amount * 0.05,  # 5% platform fee
        "final_amount": total_amount * 1.05,
    }

    return render(request, "marketplace/cart.html", context)


@login_required
def checkout(request):
    """Checkout and order creation"""
    if not request.user.is_farmer:
        return redirect("dashboard:redirect")

    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("marketplace:home")

    if request.method == "POST":
        # Create order
        total_amount = 0
        for product_id, item in cart.items():
            total_amount += item["quantity"] * item["price"]

        commission_amount = total_amount * 0.05  # 5% platform commission
        final_amount = total_amount + commission_amount

        order = Order.objects.create(
            farmer=request.user,
            total_amount=final_amount,
            commission_amount=commission_amount,
            delivery_address=request.POST.get("delivery_address"),
            delivery_phone=request.POST.get("delivery_phone"),
            notes=request.POST.get("notes", ""),
        )

        # Create order items
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["quantity"],
                unit_price=item["price"],
                total_price=item["quantity"] * item["price"],
            )

            # Update stock
            product.stock_quantity -= item["quantity"]
            product.save()

        # Clear cart
        request.session["cart"] = {}
        request.session.modified = True

        messages.success(request, f"Order #{order.order_number} placed successfully!")
        return redirect("marketplace:order_detail", order_id=order.id)

    # GET request - show checkout form
    try:
        farmer_profile = FarmerProfile.objects.get(user=request.user)
        default_address = farmer_profile.farm_location
        default_phone = request.user.phone
    except FarmerProfile.DoesNotExist:
        default_address = ""
        default_phone = ""

    context = {
        "default_address": default_address,
        "default_phone": default_phone,
    }

    return render(request, "marketplace/checkout.html", context)


@login_required
def order_history(request):
    """Farmer's order history"""
    if not request.user.is_farmer:
        return redirect("dashboard:redirect")

    orders = Order.objects.filter(farmer=request.user).order_by("-created_at")

    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    orders_page = paginator.get_page(page_number)

    context = {
        "orders": orders_page,
    }

    return render(request, "marketplace/order_history.html", context)


@login_required
def order_detail(request, order_id):
    """Individual order detail"""
    order = get_object_or_404(Order, id=order_id, farmer=request.user)

    context = {
        "order": order,
    }

    return render(request, "marketplace/order_detail.html", context)


@login_required
def cart_count(request):
    """AJAX endpoint to get cart item count"""
    cart = request.session.get("cart", {})
    count = sum(item["quantity"] for item in cart.values())
    return JsonResponse({"count": count})
