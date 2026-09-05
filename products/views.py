
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from decimal import Decimal
from django.contrib.auth import update_session_auth_hash

import razorpay

from .models import Product, ProductImage, CartItem, Order, OrderItem,  Wishlist, Address


# =====================================================
# RAZORPAY CLIENT
# =====================================================

razorpay_client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)


def loading(request):
    return render(request, "products/loading.html")

@login_required
def help_support(request):
    return render(
        request,
        "products/help_support.html"
    )

# =====================================================
# HOME
# =====================================================
from django.db import models
from django.shortcuts import render

def home(request):

    products = Product.objects.all()

    # ==============================
    # SEARCH
    # ==============================

    search = request.GET.get("search", "").strip()

    if search:
        products = products.filter(
            models.Q(name__icontains=search) |
            models.Q(brand__icontains=search) |
            models.Q(category__icontains=search)
        )

    # ==============================
    # CATEGORY
    # ==============================

    category = request.GET.get("category", "").strip()

    if category in ["men", "women", "kids"]:
        products = products.filter(
            category=category
        )

    # ==============================
    # PRICE FILTER
    # ==============================

    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    if min_price:
        try:
            products = products.filter(
                price__gte=float(min_price)
            )
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(
                price__lte=float(max_price)
            )
        except ValueError:
            pass

    # ==============================
    # DISCOUNT FILTER
    # ==============================

    discount = request.GET.get("discount", "").strip()

    if discount:
        try:
            products = products.filter(
                discount__gte=int(discount)
            )
        except ValueError:
            pass

    # ==============================
    # SORT
    # ==============================

    sort = request.GET.get("sort", "").strip()

    if sort == "price_low":
        products = products.order_by("price")

    elif sort == "price_high":
        products = products.order_by("-price")

    elif sort == "discount":
        products = products.order_by("-discount")

    else:
        products = products.order_by("-created_at")

    # ==============================
    # SEND DATA TO HOME.HTML
    # ==============================

    return render(
        request,
        "products/home.html",
        {
            "products": products,
            "search": search,
        }
    )

# =====================================================
# MEN
# =====================================================

def men(request):
    products = Product.objects.filter(category="men")

    return render(
        request,
        "products/home.html",
        {
            "products": products,
            "search": "",
        }
    )


# =====================================================
# WOMEN
# =====================================================

def women(request):
    products = Product.objects.filter(
        category="women"
    ).order_by("-created_at")

    return render(
        request,
        "products/women.html",
        {
            "products": products
        }
    )


# =====================================================
# KIDS
# =====================================================

def kids(request):
    products = Product.objects.filter(
        category="kids"
    ).order_by("-created_at")

    return render(
        request,
        "products/kids.html",
        {
            "products": products
        }
    )


# =====================================================
# PRODUCT DETAIL
# =====================================================

def product_detail(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    sizes = []

    if product.size:
        sizes = [
            size.strip()
            for size in product.size.split(",")
            if size.strip()
        ]

    extra_images = ProductImage.objects.filter(
        product=product
    )

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "sizes": sizes,
            "extra_images": extra_images,
        }
    )


# =====================================================
# PROFILE
# =====================================================

@login_required
def profile(request):

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    total_orders = Order.objects.filter(
        user=request.user
    ).count()

    address_count = 0

    return render(
        request,
        "products/profile.html",
        {
            "wishlist_count": wishlist_count,
            "total_orders": total_orders,
            "address_count": address_count,
        }
    )

# =====================================================
# ADD TO CART
# =====================================================

@login_required
def add_to_cart(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    if request.method != "POST":
        return redirect(
            "product_detail",
            id=product.id
        )

    size = request.POST.get(
        "size",
        "Free Size"
    )

    quantity_text = request.POST.get(
        "quantity",
        "1"
    )

    try:
        quantity = int(quantity_text)

        if quantity < 1:
            quantity = 1

    except (ValueError, TypeError):
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        size=size,
        defaults={
            "quantity": quantity
        }
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    # BUY NOW
    if request.POST.get("buy_now"):
        request.session["buy_now_item"] = cart_item.id

        return redirect("checkout")

    # AJAX
    if request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest":

        total_items = CartItem.objects.filter(
            user=request.user
        ).count()

        return JsonResponse({
            "success": True,
            "message": "Product added to cart!",
            "cart_count": total_items
        })

    return redirect("cart")

@login_required
def edit_profile(request):
    return render(request, "edit_profile.html")


@login_required
def edit_address(request):
    return render(request, "address.html")


@login_required
def delete_address(request):
    return redirect("address")

@login_required
def settings_page(request):
    return render(request, "settings.html")
    
# =====================================================
# CART
# =====================================================

@login_required
def cart(request):

    cart_items = CartItem.objects.filter(
        user=request.user
    ).select_related(
        "product"
    ).order_by("-created_at")

    total = Decimal("0.00")

    for item in cart_items:

        item.subtotal = (
            item.product.price *
            item.quantity
        )

        total += item.subtotal

    total_items = sum(
        item.quantity
        for item in cart_items
    )

    return render(
        request,
        "products/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
            "total_items": total_items,
        }
    )


# =====================================================
# UPDATE CART QUANTITY
# =====================================================

@login_required
def update_cart_quantity(request):

    if request.method != "POST":

        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        })

    cart_id = request.POST.get("cart_id")
    action = request.POST.get("action")

    try:

        item = CartItem.objects.get(
            id=cart_id,
            user=request.user
        )

        if action == "plus":

            item.quantity += 1

        elif action == "minus":

            if item.quantity > 1:
                item.quantity -= 1

        else:

            return JsonResponse({
                "success": False,
                "message": "Invalid action."
            })

        item.save()

        cart_items = CartItem.objects.filter(
            user=request.user
        ).select_related(
            "product"
        )

        total = sum(
            item.product.price *
            item.quantity
            for item in cart_items
        )

        total_items = sum(
            item.quantity
            for item in cart_items
        )

        return JsonResponse({
            "success": True,
            "quantity": item.quantity,
            "total": str(total),
            "total_items": total_items,
        })

    except CartItem.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "Cart item not found."
        })


# =====================================================
# REMOVE FROM CART
# =====================================================

@login_required
def remove_from_cart(request, cart_id):

    item = get_object_or_404(
        CartItem,
        id=cart_id,
        user=request.user
    )

    item.delete()

    return redirect("cart")


# =====================================================
# CHECKOUT
# =====================================================

@login_required
def checkout(request):

    buy_now_item_id = request.session.get("buy_now_item")

    # =====================================================
    # BUY NOW
    # =====================================================

    if buy_now_item_id:

        try:
            cart_item = CartItem.objects.select_related(
                "product"
            ).get(
                id=buy_now_item_id,
                user=request.user
            )

            cart_items = [cart_item]

        except CartItem.DoesNotExist:

            request.session.pop("buy_now_item", None)

            messages.error(
                request,
                "Buy Now product was not found."
            )

            return redirect("cart")

    # =====================================================
    # NORMAL CART CHECKOUT
    # =====================================================

    else:

        cart_items = list(
            CartItem.objects.filter(
                user=request.user
            ).select_related("product")
        )

    # =====================================================
    # EMPTY CHECK
    # =====================================================

    if not cart_items:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    # =====================================================
    # STOCK CHECK
    # =====================================================

    for item in cart_items:

        if item.quantity > item.product.stock:

            messages.error(
                request,
                f"Sorry! {item.product.name} has only "
                f"{item.product.stock} item(s) available."
            )

            return redirect("cart")

    # =====================================================
    # TOTAL
    # =====================================================

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render(
        request,
        "products/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
        }
    )

# =====================================================
# PLACE ORDER
# =====================================================

@login_required
def place_order(request):

    if request.method != "POST":
        return redirect("checkout")

    # =====================================================
    # DELIVERY DETAILS
    # =====================================================

    full_name = request.POST.get("full_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()
    city = request.POST.get("city", "").strip()
    state = request.POST.get("state", "").strip()
    pincode = request.POST.get("pincode", "").strip()

    payment_method = request.POST.get(
        "payment_method",
        "cod"
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    if not all([
        full_name,
        phone,
        address,
        city,
        state,
        pincode
    ]):

        messages.error(
            request,
            "Please fill all delivery details."
        )

        return redirect("checkout")

    # =====================================================
    # BUY NOW / NORMAL CART
    # =====================================================

    buy_now_item_id = request.session.get(
        "buy_now_item"
    )

    if buy_now_item_id:

        try:

            cart_item = CartItem.objects.select_related(
                "product"
            ).get(
                id=buy_now_item_id,
                user=request.user
            )

            cart_items = [cart_item]

        except CartItem.DoesNotExist:

            request.session.pop(
                "buy_now_item",
                None
            )

            messages.error(
                request,
                "Buy Now product was not found."
            )

            return redirect("cart")

    else:

        cart_items = list(
            CartItem.objects.filter(
                user=request.user
            ).select_related("product")
        )

    # =====================================================
    # EMPTY CART
    # =====================================================

    if not cart_items:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    # =====================================================
    # STOCK CHECK
    # =====================================================

    for item in cart_items:

        if item.quantity > item.product.stock:

            messages.error(
                request,
                f"Sorry! {item.product.name} has only "
                f"{item.product.stock} item(s) available."
            )

            return redirect("cart")

    # =====================================================
    # TOTAL
    # =====================================================

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    # =====================================================
    # COD ORDER
    # =====================================================

    if payment_method == "cod":

        order = Order.objects.create(

            user=request.user,

            full_name=full_name,

            phone=phone,

            address=address,

            city=city,

            state=state,

            pincode=pincode,

            total_amount=total,

            payment_method="cod",

            payment_status="pending",

            order_status="confirmed",
        )

        # -------------------------------------------------
        # CREATE ORDER ITEMS + REDUCE STOCK
        # -------------------------------------------------

        for item in cart_items:

            OrderItem.objects.create(

                order=order,

                product=item.product,

                quantity=item.quantity,

                price=item.product.price,
            )

            # Reduce product stock
            item.product.stock -= item.quantity

            item.product.save(
                update_fields=["stock"]
            )

        # -------------------------------------------------
        # DELETE CART ITEMS
        # -------------------------------------------------

        for item in cart_items:
            item.delete()

        # Remove Buy Now session
        request.session.pop(
            "buy_now_item",
            None
        )

        return redirect(
            "order_success",
            order_id=order.id
        )

    # =====================================================
    # ONLINE PAYMENT
    # =====================================================

    if payment_method == "online":

        order = Order.objects.create(

            user=request.user,

            full_name=full_name,

            phone=phone,

            address=address,

            city=city,

            state=state,

            pincode=pincode,

            total_amount=total,

            payment_method="online",

            payment_status="pending",

            order_status="pending",
        )

        # -------------------------------------------------
        # CREATE ORDER ITEMS
        # -------------------------------------------------

        for item in cart_items:

            OrderItem.objects.create(

                order=order,

                product=item.product,

                quantity=item.quantity,

                price=item.product.price,
            )

        # -------------------------------------------------
        # RAZORPAY AMOUNT
        # -------------------------------------------------

        amount = int(
            Decimal(str(total)) * 100
        )

        # -------------------------------------------------
        # CREATE RAZORPAY ORDER
        # -------------------------------------------------

        try:

            razorpay_order = razorpay_client.order.create(
                data={
                    "amount": amount,
                    "currency": "INR",
                    "receipt": f"order_{order.id}",
                }
            )

        except Exception as e:

            order.delete()

            messages.error(
                request,
                f"Unable to start online payment: {str(e)}"
            )

            return redirect("checkout")

        # -------------------------------------------------
        # SAVE RAZORPAY ORDER ID
        # -------------------------------------------------

        order.razorpay_order_id = (
            razorpay_order["id"]
        )

        order.save(
            update_fields=[
                "razorpay_order_id"
            ]
        )

        # -------------------------------------------------
        # SAVE ORDER ID IN SESSION
        # -------------------------------------------------

        request.session["online_order_id"] = (
            order.id
        )

        # -------------------------------------------------
        # PAYMENT PAGE
        # -------------------------------------------------

        return render(
            request,
            "products/payment.html",
            {
                "order": order,

                "razorpay_key":
                    settings.RAZORPAY_KEY_ID,

                "razorpay_order_id":
                    razorpay_order["id"],

                "amount":
                    amount,

                "total":
                    total,

                "order_items":
                    order.items.all(),
            }
        )

    # =====================================================
    # INVALID PAYMENT METHOD
    # =====================================================

    messages.error(
        request,
        "Invalid payment method."
    )

    return redirect("checkout")
# =====================================================
# PAYMENT SUCCESS
# =====================================================

@login_required
def payment_success(request):

    # =====================================================
    # GET ORDER FROM SESSION
    # =====================================================

    order_id = request.session.get(
        "online_order_id"
    )

    if not order_id:

        messages.error(
            request,
            "Payment order not found."
        )

        return redirect("checkout")

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # =====================================================
    # PAYMENT DETAILS
    # =====================================================

    payment_id = request.GET.get(
        "razorpay_payment_id"
    )

    razorpay_order_id = request.GET.get(
        "razorpay_order_id"
    )

    razorpay_signature = request.GET.get(
        "razorpay_signature"
    )

    # =====================================================
    # CHECK PAYMENT DETAILS
    # =====================================================

    if not all([
        payment_id,
        razorpay_order_id,
        razorpay_signature
    ]):

        order.payment_status = "failed"
        order.save(
            update_fields=["payment_status"]
        )

        messages.error(
            request,
            "Payment verification details are missing."
        )

        return redirect("checkout")

    # =====================================================
    # VERIFY RAZORPAY PAYMENT
    # =====================================================

    try:

        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id":
                razorpay_order_id,

            "razorpay_payment_id":
                payment_id,

            "razorpay_signature":
                razorpay_signature,
        })

    except Exception:

        order.payment_status = "failed"

        order.save(
            update_fields=["payment_status"]
        )

        messages.error(
            request,
            "Payment verification failed."
        )

        return redirect("checkout")

    # =====================================================
    # CHECK STOCK AGAIN
    # =====================================================

    order_items = order.items.select_related(
        "product"
    )

    for item in order_items:

        if item.quantity > item.product.stock:

            order.payment_status = "paid"
            order.order_status = "pending"

            order.save(
                update_fields=[
                    "payment_status",
                    "order_status",
                ]
            )

            messages.error(
                request,
                f"Sorry! {item.product.name} is "
                f"no longer available in the required quantity."
            )

            return redirect("orders")

    # =====================================================
    # REDUCE STOCK
    # =====================================================

    for item in order_items:

        item.product.stock -= item.quantity

        item.product.save(
            update_fields=["stock"]
        )

    # =====================================================
    # UPDATE ORDER
    # =====================================================

    order.razorpay_payment_id = payment_id

    order.razorpay_order_id = razorpay_order_id

    order.payment_status = "paid"

    order.order_status = "confirmed"

    order.save()

    # =====================================================
    # REMOVE ORDERED ITEMS FROM CART
    # =====================================================

    for item in order_items:

        CartItem.objects.filter(
            user=request.user,
            product=item.product
        ).delete()

    # =====================================================
    # CLEAR SESSIONS
    # =====================================================

    request.session.pop(
        "online_order_id",
        None
    )

    request.session.pop(
        "buy_now_item",
        None
    )

    # =====================================================
    # SUCCESS
    # =====================================================

    return redirect(
        "order_success",
        order_id=order.id
    )

# =====================================================
# ORDER SUCCESS
# =====================================================

@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "products/order_success.html",
        {
            "order": order
        }
    )


# =====================================================
# MY ORDERS
# =====================================================

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        "items"
    ).order_by("-id")

    return render(
        request,
        "products/my_orders.html",
        {
            "orders": orders
        }
    )


# =====================================================
# ORDERS
# =====================================================

@login_required
def orders(request):

    return redirect("my_orders")


# =====================================================
# DELETE ORDER
# =====================================================

@login_required
def delete_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if request.method == "POST":

        order.delete()

        messages.success(
            request,
            "Order deleted successfully."
        )

    return redirect("my_orders")

# =====================================================
# WISHLIST
# =====================================================


@login_required
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product").order_by("-created_at")

    return render(
        request,
        "products/wishlist.html",
        {
            "wishlist_items": wishlist_items
        }
    )


# =====================================================
# ADD TO WISHLIST
# =====================================================

@login_required
def add_to_wishlist(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("wishlist")


# =====================================================
# ADD TO WISHLIST
# =====================================================

# =====================================================
# REMOVE FROM WISHLIST
# =====================================================


@login_required
def remove_from_wishlist(request, wishlist_id):

    item = get_object_or_404(
        Wishlist,
        id=wishlist_id,
        user=request.user
    )

    item.delete()

    return redirect("wishlist")


# =====================================================
# ADDRESS
# =====================================================

@login_required
def address(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        address_text = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        landmark = request.POST.get("landmark", "").strip()

        # Required fields check
        if not full_name or not mobile or not address_text or not city or not state or not pincode:
            return render(
                request,
                "products/address.html",
                {
                    "error": "Please fill all required fields."
                }
            )

        Address.objects.create(
            user=request.user,
            full_name=full_name,
            mobile=mobile,
            address=address_text,
            city=city,
            state=state,
            pincode=pincode,
            landmark=landmark
        )

        return redirect("address")

    addresses = Address.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "products/address.html",
        {
            "addresses": addresses
        }
    )

# =====================================================
# NOTIFICATIONS
# =====================================================

@login_required
def notifications(request):

    return render(
        request,
        "products/notifications.html"
    )



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def edit_profile(request):

    user = request.user

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        if username:
            user.username = username

        if email:
            user.email = email

        user.save()

        messages.success(request, "Profile updated successfully!")

        return redirect("profile")

    return render(
        request,
        "products/edit_profile.html",
        {
            "user": user
        }
    )

@login_required
def edit_address(request, id):
    address_obj = get_object_or_404(
        Address,
        id=id,
        user=request.user
    )

    if request.method == "POST":
        address_obj.full_name = request.POST.get("full_name")
        address_obj.mobile = request.POST.get("mobile")
        address_obj.address = request.POST.get("address")
        address_obj.city = request.POST.get("city")
        address_obj.state = request.POST.get("state")
        address_obj.pincode = request.POST.get("pincode")
        address_obj.landmark = request.POST.get("landmark")

        address_obj.save()

        return redirect("address")

    return render(
        request,
        "edit_address.html",
        {"address": address_obj}
    )

@login_required
def edit_address(request, id):
    address_obj = get_object_or_404(
        Address,
        id=id,
        user=request.user
    )

    if request.method == "POST":
        address_obj.full_name = request.POST.get("full_name")
        address_obj.mobile = request.POST.get("mobile")
        address_obj.address = request.POST.get("address")
        address_obj.city = request.POST.get("city")
        address_obj.state = request.POST.get("state")
        address_obj.pincode = request.POST.get("pincode")
        address_obj.landmark = request.POST.get("landmark")

        address_obj.save()

        return redirect("address")

    return render(
        request,
        "edit_address.html",
        {"address": address_obj}
    )


@login_required
def delete_address(request, id):
    address_obj = get_object_or_404(
        Address,
        id=id,
        user=request.user
    )

    if request.method == "POST":
        address_obj.delete()

    return redirect("address")


# =====================================================
# CHANGE PASSWORD
# =====================================================
@login_required
def change_password(request):

    if request.method == "POST":

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Current password check
        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("change_password")

        # New password match check
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password")

        # Password length
        if len(new_password) < 8:
            messages.error(
                request,
                "New password must be at least 8 characters."
            )
            return redirect("change_password")

        # Save new password
        request.user.set_password(new_password)
        request.user.save()

        # Keep user logged in
        update_session_auth_hash(request, request.user)

        messages.success(
            request,
            "Password changed successfully!"
        )

        return redirect("profile")

    return render(
        request,
        "products/change_password.html"
    )

# =====================================================
# ORDER UPDATES
# =====================================================

@login_required
def order_updates(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "products/order_updates.html",
        {
            "orders": orders
        }
    )
# =====================================================
# OFFERS
# =====================================================

def offers(request):
    products = Product.objects.filter(
        discount__gt=0
    ).order_by("-discount")

    return render(
        request,
        "products/offers.html",
        {"products": products}
    )


# =====================================================
# PREFERENCES
# =====================================================

@login_required
def preferences(request):

    return render(
        request,
        "products/preferences.html"
    )


# =====================================================
# THEME
# =====================================================

@login_required
def theme(request):
    if request.method == "POST":
        selected_theme = request.POST.get("theme")

        if selected_theme in ["light", "dark"]:
            request.session["theme"] = selected_theme

        return redirect("theme")

    current_theme = request.session.get("theme", "light")

    return render(request, "products/theme.html", {
        "current_theme": current_theme
    })

# =====================================================
# LANGUAGE
# =====================================================

@login_required
def language(request):

    if request.method == "POST":

        selected_language = request.POST.get("language")

        if selected_language in [
            "english",
            "hindi",
            "gujarati",
            "marathi"
        ]:
            request.session["language"] = selected_language

        return redirect("language")

    current_language = request.session.get(
        "language",
        "english"
    )

    return render(
        request,
        "products/language.html",
        {
            "current_language": current_language
        }
    )

# =====================================================
# PRIVACY & SECURITY
# =====================================================
@login_required
def privacy_security(request):
    return render(
        request,
        "products/privacy_security.html"
    )

# =====================================================
# SECURITY
# =====================================================

@login_required
def security(request):

    return render(
        request,
        "products/security.html"
    )


# =====================================================
# DELETE ACCOUNT
# =====================================================

@login_required
def delete_account(request):

    if request.method == "POST":

        password = request.POST.get("password")

        if not request.user.check_password(password):
            messages.error(
                request,
                "Incorrect password. Account was not deleted."
            )
            return redirect("delete_account")

        user = request.user

        logout(request)
        user.delete()

        messages.success(
            request,
            "Your account has been deleted successfully."
        )

        return redirect("home")

    return render(
        request,
        "products/delete_account.html"
    )

# =====================================================
# HELP & SUPPORT
# =====================================================

def help_support(request):

    return render(
        request,
        "products/help.html"
    )


# =====================================================
# CONTACT
# =====================================================

def contact(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        messages.success(
            request,
            "Your message has been sent successfully!"
        )

        return redirect("contact")

    return render(request, "products/contact.html")


# =====================================================
# ABOUT
# =====================================================

def about(request):
    return render(request, "products/about.html")

# =====================================================
# REGISTER
# =====================================================

def register(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # PASSWORD CHECK

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")

        # USERNAME CHECK

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")

        # EMAIL CHECK

        if email and User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return redirect("register")

        # CREATE USER

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect("login")

    return render(
        request,
        "products/register.html"
    )