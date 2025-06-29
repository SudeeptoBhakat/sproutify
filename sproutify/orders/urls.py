from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    view_cart_page,
    get_cart_items_api,
    OrderAPI, UserOrderItemsAPI,
    PaymentMethodViewSet, PaymentViewSet, InvoiceDetailAPIView, OrderTrackingAPIView
)
from orders import views

router = DefaultRouter()
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'payments', PaymentViewSet)
# router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart_page, name='view-cart-page'),  # HTML page
    path('api/cart/', views.get_cart_items_api, name='cart-items-api'),  # API endpoint
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    path('cart/delete/<int:pk>/', views.delete_cart_item, name='delete_cart_item'),

    path('api/create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('api/verify-payment/', views.verify_payment, name='verify_payment'),

    path('orders/', views.view_order_page, name='view-orders-page'),
    path('api/orders/', OrderAPI.as_view(), name='get-user-orders'),

    path("api/user-orders-items/", UserOrderItemsAPI.as_view(), name="user-orders-items"),

    path('api/tracking/<int:order_id>/', OrderTrackingAPIView.as_view(), name='order-tracking'),

    path('api/invoice/<int:order_id>/', InvoiceDetailAPIView.as_view(), name='invoice-detail'),
] 
