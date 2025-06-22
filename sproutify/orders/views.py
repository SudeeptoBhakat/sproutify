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
from .models import Cart
from users.models import Product
from .serializers import CartSerializer

def view_cart_page(request):
    return render(request, 'basket.html')

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    # print(product_id, quantity)

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
        cart_item.save()

    serializer = CartSerializer(cart_item)
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

    quantity = request.data.get("quantity")
    if quantity:
        cart_item.quantity = int(quantity)
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

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_razorpay_order(request):
    try:
        user = request.user
        amount = float(request.data.get("amount"))  # from JS
        final_amount = int(amount * 100)  # Razorpay needs paise
        
        # create dummy order
        order = Order.objects.create(
            user=user,
            shipping_full_name=request.data.get("full_name"),
            shipping_phone=request.data.get("phone"),
            shipping_state=request.data.get("state"),
            shipping_district=request.data.get("district"),
            shipping_address_line1=request.data.get("address_line1"),
            shipping_street=request.data.get("street"),
            shipping_pin_code=request.data.get("pin"),
            total_amount=amount,
            discount=0,
            shipping_charge=0,
            final_amount=amount,
            notes=request.data.get("notes", "")
        )

        razorpay_order = razorpay_client.order.create({
            "amount": final_amount,
            "currency": "INR",
            "receipt": f"order_rcptid_{order.id}",
            "payment_capture": 1
        })

        # Save Payment Entry
        payment = Payment.objects.create(
            order=order,
            user=user,
            transaction_id=razorpay_order['id'],
            amount=amount,
            method=PaymentMethod.objects.filter(name="Online", provider="Razorpay").first(),
            status='initiated',
            created_at=timezone.now()
        )

        return Response({
            "order_id": razorpay_order['id'],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": final_amount,
            "order_db_id": order.id,
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
        order_db_id = data.get("order_db_id")

        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        }

        # Verify Signature
        razorpay_client.utility.verify_payment_signature(params_dict)

        # Update payment record
        payment = Payment.objects.get(transaction_id=razorpay_order_id)
        payment.status = "successful"
        payment.paid_at = timezone.now()
        payment.response_data = data
        payment.save()

        # Mark Order as Paid
        order = payment.order
        order.is_paid = True
        order.status = 'processing'
        order.save()

        return Response({"message": "Payment Successful"})

    except Exception as e:
        try:
            payment = Payment.objects.get(transaction_id=data.get("razorpay_order_id"))
            payment.status = "failed"
            payment.response_data = {"error": str(e)}
            payment.save()
        except:
            pass
        return Response({"error": "Payment Verification Failed"}, status=status.HTTP_400_BAD_REQUEST)




class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

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