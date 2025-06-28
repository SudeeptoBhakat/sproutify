from django.contrib import admin
from .models import Cart, Order, OrderItem, PaymentMethod, Payment, Invoice, OrderTracking

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'order_status', 'is_active', 'added_at')
    list_filter = ('order_status', 'is_active')
    search_fields = ('user__email', 'product__name')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'shipping_full_name', 'status', 'total_amount', 'final_amount', 'is_paid', 'ordered_at']
    search_fields = ['user__email', 'shipping_name', 'shipping_address_line1']
    list_filter = ['status', 'is_paid']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_order', 'total_price')
    readonly_fields = ('order', 'product', 'quantity', 'price_at_order', 'total_price')

    # def has_add_permission(self, request):
    #     return False  # Disable adding new order items from admin

    # def has_change_permission(self, request, obj=None):
    #     return False  # Disable editing order items

    # def has_delete_permission(self, request, obj=None):
    #     return False  # Optional: disable deletion


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'is_active')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'status', 'transaction_id', 'amount', 'paid_at')
    list_filter = ('status',)
    search_fields = ('transaction_id',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('order', 'invoice_number', 'created_at')


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'tracking_number', 'carrier', 'status', 'estimated_delivery')
