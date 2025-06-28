from django.db import models
from django.conf import settings
from users.models import Product, CustomUser  # Ensure Address exists and holds shipping info


# ------------------------ CART MODEL ------------------------

class Cart(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_entries'
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    order_status = models.CharField(
        max_length=10,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product', 'order_status')

    def __str__(self):
        return f"{self.user} - {self.product.name} x {self.quantity} ({self.order_status})"

    def save(self, *args, **kwargs):
        if not self.price_at_time:
            self.price_at_time = self.product.price
        self.total_price = self.price_at_time * self.quantity
        super().save(*args, **kwargs)


# ------------------------ ORDER MODELS ------------------------

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    # Shipping Info (copied from user at time of order)
    shipping_full_name = models.CharField(max_length=200)
    shipping_phone = models.CharField(max_length=15)
    shipping_state = models.CharField(max_length=100)
    shipping_district = models.CharField(max_length=100)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_street = models.CharField(max_length=255)
    shipping_pin_code = models.CharField(max_length=10)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2)  # = total - discount + shipping
    notes = models.TextField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-ordered_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.email} - {self.status}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=False)
    quantity = models.PositiveIntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        product_name = self.product.name if self.product else "Unknown Product"
        return f"{product_name} x {self.quantity}"


    def save(self, *args, **kwargs):
        self.total_price = self.price_at_order * self.quantity
        super().save(*args, **kwargs)


# ------------------------ PAYMENT MODELS ------------------------

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)  # e.g., Credit Card, UPI, COD
    provider = models.CharField(max_length=50, blank=True, null=True)  # e.g., Razorpay, Stripe
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('initiated', 'Initiated'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='initiated')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(blank=True, null=True)
    response_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.status}"


# ------------------------ INVOICE MODEL ------------------------

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)

    def __str__(self):
        return f"Invoice {self.invoice_number}"


# ------------------------ ORDER TRACKING ------------------------

class OrderTracking(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='tracking')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    carrier = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, default='Order Placed')  # e.g., 'Shipped', 'In Transit'
    estimated_delivery = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tracking #{self.tracking_number or 'N/A'} ({self.status})"
