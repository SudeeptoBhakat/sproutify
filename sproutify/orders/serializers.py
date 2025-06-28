from rest_framework import serializers
from .models import Cart, Order, OrderItem, PaymentMethod, Payment, Invoice, OrderTracking


class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.CharField(source='product.image', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product','product_image', 'product_name', 'product_price', 'quantity', 'price_at_time', 'total_price', 'order_status', 'notes', 'added_at']
        read_only_fields = ['user', 'price_at_time', 'total_price', 'added_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'product_image', 'quantity', 'price_at_order', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'shipping_full_name', 'shipping_state', 'shipping_district',
            'shipping_address_line1', 'shipping_street', 'shipping_pin_code',
            'status', 'total_amount', 'discount', 'shipping_charge', 'final_amount',
            'notes', 'is_paid', 'ordered_at', 'updated_at', 'items'
        ]
        read_only_fields = ['is_paid', 'ordered_at', 'updated_at', 'final_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = validated_data['user']

        # Fallback to user info if shipping not provided
        for field in ['shipping_name', 'shipping_state', 'shipping_district',
                      'shipping_address_line1', 'shipping_street', 'shipping_pin_code']:
            if not validated_data.get(field):
                validated_data[field] = getattr(user, field.replace('shipping_', ''), '')

        # Calculate total
        total = sum(item['price_at_order'] * item['quantity'] for item in items_data)
        validated_data['total_amount'] = total
        validated_data['final_amount'] = total - validated_data.get('discount', 0) + validated_data.get('shipping_charge', 0)

        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    order = serializers.StringRelatedField(read_only=True)
    method = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'user', 'method',
            'status', 'transaction_id', 'amount',
            'paid_at', 'created_at'
        ]
        read_only_fields = ['status', 'transaction_id', 'paid_at', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = '__all__'
