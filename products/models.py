from django.db import models
from django.contrib.auth.models import User


# =====================================================
# PRODUCT
# =====================================================

class Product(models.Model):

    CATEGORY_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("kids", "Kids"),
    ]

    FIT_CHOICES = [
        ("regular", "Regular Fit"),
        ("slim", "Slim Fit"),
        ("oversized", "Oversized"),
        ("relaxed", "Relaxed Fit"),
    ]

    name = models.CharField(max_length=200)

    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="men"
    )

    brand = models.CharField(
        max_length=100,
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    discount = models.PositiveIntegerField(
        default=0
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    color = models.CharField(
        max_length=50,
        blank=True
    )

    fabric = models.CharField(
        max_length=100,
        blank=True
    )

    size = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: S,M,L,XL"
    )

    fit = models.CharField(
        max_length=30,
        choices=FIT_CHOICES,
        blank=True
    )

    pattern = models.CharField(
        max_length=100,
        blank=True
    )

    sleeve = models.CharField(
        max_length=100,
        blank=True
    )

    occasion = models.CharField(
        max_length=100,
        blank=True
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0
    )

    reviews_count = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


# =====================================================
# PRODUCT EXTRA IMAGES
# =====================================================

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/"
    )

    def __str__(self):
        return self.product.name


# =====================================================
# CART
# =====================================================

class CartItem(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    size = models.CharField(
        max_length=20
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"


# =====================================================
# ORDER
# =====================================================
# =====================================================
# ORDER
# =====================================================

class Order(models.Model):

    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("online", "Online Payment"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=200
    )

    phone = models.CharField(
        max_length=15
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="cod"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    order_status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS_CHOICES,
        default="pending"
    )

    razorpay_order_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id}"
# =====================================================
# ORDER ITEM
# =====================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} - Order #{self.order.id}"



# =====================================================
# WISHLIST
# =====================================================

class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    full_name = models.CharField(max_length=150)

    mobile = models.CharField(max_length=15)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    landmark = models.CharField(
        max_length=150,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.full_name} - {self.city}"