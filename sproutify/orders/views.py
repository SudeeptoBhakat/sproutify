from datetime import timedelta
from django.utils.timezone import now
from django.shortcuts import render
from rest_framework import viewsets
from .models import Cart, Order, OrderItem, PaymentMethod, Payment, Invoice, OrderTracking
from .serializers import (
    CartSerializer, OrderSerializer, OrderItemSerializer,
    PaymentMethodSerializer, PaymentSerializer,
    InvoiceSerializer, OrderTrackingSerializer
)

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart
from users.models import Product
from .serializers import CartSerializer

def view_cart_page(request):
    return render(request, 'basket.html')

@api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    print(product_id, quantity)
    print("AUTH HEADER:", request.headers.get("Authorization"))
    print("User:", request.user)
    print("User Authenticated:", request.user.is_authenticated)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=product,
        order_status='pending',
        defaults={'quantity': quantity, 'price_at_time': product.price}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.is_active = True
        cart_item.save()

    serializer = CartSerializer(cart_item)
    print("data", serializer.data)
    return Response({"message": "Product added to cart successfully", "data":serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_cart_items_api(request):
    cart_items = Cart.objects.filter(user=request.user, order_status='pending', is_active=True)
    total = sum(item.total_price for item in cart_items)
    discount = 100 if total > 1000 else 0
    final_total = total - discount
    delivery_start = now().date() + timedelta(days=3)
    delivery_end = delivery_start + timedelta(days=2)

    serializer = CartSerializer(cart_items, many=True)
    return Response({
        "items": serializer.data,
        "total": total,
        "discount": discount,
        "final_total": final_total,
        "delivery_start": delivery_start.strftime('%b %d'),
        "delivery_end": delivery_end.strftime('%b %d'),
        "user": {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "street": request.user.street,
            "address_line1": request.user.address_line1,
            "district": request.user.district,
            "state": request.user.state,
            "pin_code": request.user.pin_code,
        }
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, pk):
    try:
        cart_item = Cart.objects.get(pk=pk, user=request.user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get("quantity_action")

    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
        
    cart_item.save()

    serializer = CartSerializer(cart_item)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_cart_item(request, pk):
    try:
        cart_item = Cart.objects.get(pk=pk, user=request.user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

    cart_item.quantity = 0
    cart_item.is_active = False
    cart_item.save()
    return Response({"message": "Cart item removed."}, status=status.HTTP_204_NO_CONTENT)



# orders/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from .models import Order, Payment, PaymentMethod
from django.conf import settings
import razorpay
import uuid


from django.db import transaction
from django.utils import timezone
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from orders.models import Order, OrderItem, Payment, PaymentMethod, Invoice, OrderTracking
from users.models import Product
import razorpay
import uuid

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_razorpay_order(request):
    try:
        user = request.user
        cart = request.data.get("cart", [])
        shipping = request.data.get("shipping", {})
        notes = request.data.get("notes", "")
        amount = float(request.data.get("amount"))
        final_amount = int(amount * 100)  # Razorpay needs paise

        # Step 1: Create Order & Items atomically
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                shipping_full_name=shipping.get("full_name"),
                shipping_phone=shipping.get("phone"),
                shipping_state=shipping.get("state"),
                shipping_district=shipping.get("district"),
                shipping_address_line1=shipping.get("address_line1"),
                shipping_street=shipping.get("street"),
                shipping_pin_code=shipping.get("pin_code"),
                total_amount=amount,
                discount=0,
                shipping_charge=0,
                final_amount=amount,
                notes=notes,
                is_paid=False,
                status='pending'
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    price_at_order=item["price"],
                    total_price=float(item["price"]) * int(item["quantity"])
                )

        # Step 2: Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": final_amount,
            "currency": "INR",
            "receipt": f"order_rcptid_{order.id}",
            "payment_capture": 1
        })

        # Step 3: Save Payment record
        Payment.objects.create(
            order=order,
            user=user,
            transaction_id=razorpay_order["id"],
            amount=amount,
            method=PaymentMethod.objects.filter(name="Online", provider="Razorpay").first(),
            status="initiated"
        )

        return Response({
            "order_id": razorpay_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": final_amount,
            "order_db_id": order.id
        })

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_payment(request):
    try:
        data = request.data
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        }

        # Verify Signature
        razorpay_client.utility.verify_payment_signature(params_dict)

        # Update Payment record
        payment = Payment.objects.get(transaction_id=razorpay_order_id)
        payment.status = "successful"
        payment.paid_at = timezone.now()
        payment.response_data = data
        payment.save()

        # Mark Order as Paid
        order = payment.order
        order.is_paid = True
        order.status = "processing"
        order.save()

        # Generate Invoice
        invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{order.id}"
        Invoice.objects.create(order=order, invoice_number=invoice_number)

        # Create OrderTracking
        OrderTracking.objects.create(
            order=order,
            status="Order Placed",
            carrier="Not Assigned",
            tracking_number=f"TRK-{uuid.uuid4().hex[:10]}"
        )

        return Response({"message": "Payment successful and order confirmed."})

    except Exception as e:
        try:
            payment = Payment.objects.get(transaction_id=request.data.get("razorpay_order_id"))
            payment.status = "failed"
            payment.response_data = {"error": str(e)}
            payment.save()
        except:
            pass
        return Response({"error": "Payment verification failed", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.none()  # avoids router errors
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class OrderTrackingViewSet(viewsets.ModelViewSet):
    queryset = OrderTracking.objects.all()
    serializer_class = OrderTrackingSerializer