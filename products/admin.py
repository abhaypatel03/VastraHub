from django.contrib import admin

from .models import (
    Product,
    ProductImage,
    CartItem,
    Order,
    OrderItem,
    Wishlist,
    Address,
)


# =========================================================
# PRODUCT IMAGE INLINE
# =========================================================

class ProductImageInline(admin.TabularInline):

    model = ProductImage
    extra = 4


# =========================================================
# PRODUCT ADMIN
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "brand",
        "category",
        "price",
        "mrp",
        "discount",
        "stock",
        "rating",
        "reviews_count",
        "created_at",
    )

    list_filter = (
        "category",
        "fit",
        "pattern",
        "occasion",
        "created_at",
    )

    search_fields = (
        "name",
        "brand",
        "sku",
        "color",
        "fabric",
    )

    list_editable = (
        "price",
        "mrp",
        "discount",
        "stock",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        ProductImageInline,
    ]


# =========================================================
# PRODUCT IMAGE ADMIN
# =========================================================

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "product",
        "image",
    )

    search_fields = (
        "product__name",
    )

    ordering = (
        "-id",
    )


# =========================================================
# ORDER ITEM INLINE
# =========================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "product",
        "quantity",
        "price",
    )

    can_delete = False


# =========================================================
# ORDER ADMIN
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "full_name",
        "phone",
        "total_amount",
        "payment_method",
        "payment_status",
        "order_status",
        "created_at",
    )

    list_filter = (
        "order_status",
        "payment_status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "full_name",
        "user__username",
        "user__email",
        "phone",
        "city",
        "state",
        "pincode",
        "razorpay_order_id",
        "razorpay_payment_id",
    )

    readonly_fields = (
        "user",
        "full_name",
        "phone",
        "address",
        "city",
        "state",
        "pincode",
        "total_amount",
        "payment_method",
        "payment_status",
        "razorpay_order_id",
        "razorpay_payment_id",
        "created_at",
    )

    list_editable = (
        "order_status",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        OrderItemInline,
    ]

    fieldsets = (
        (
            "Customer Information",
            {
                "fields": (
                    "user",
                    "full_name",
                    "phone",
                )
            },
        ),
        (
            "Delivery Address",
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "pincode",
                )
            },
        ),
        (
            "Order Information",
            {
                "fields": (
                    "total_amount",
                    "order_status",
                    "created_at",
                )
            },
        ),
        (
            "Payment Information",
            {
                "fields": (
                    "payment_method",
                    "payment_status",
                    "razorpay_order_id",
                    "razorpay_payment_id",
                )
            },
        ),
    )


# =========================================================
# ORDER ITEM ADMIN
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
    )

    search_fields = (
        "product__name",
        "order__id",
        "order__user__username",
    )

    list_filter = (
        "product",
    )

    ordering = (
        "-id",
    )


# =========================================================
# CART ADMIN
# =========================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "product",
        "size",
        "quantity",
        "created_at",
    )

    list_filter = (
        "size",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "product__name",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# WISHLIST ADMIN
# =========================================================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "product",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "product__name",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# ADDRESS ADMIN
# =========================================================

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "full_name",
        "mobile",
        "city",
        "state",
        "pincode",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "mobile",
        "city",
        "state",
        "pincode",
    )

    list_filter = (
        "state",
        "city",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "user",
        "created_at",
        "updated_at",
    )