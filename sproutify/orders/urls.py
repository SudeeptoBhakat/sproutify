from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    view_cart_page,
    get_cart_items_api,
    OrderViewSet, OrderItemViewSet,
    PaymentMethodViewSet, PaymentViewSet, InvoiceViewSet, OrderTrackingViewSet
)
from orders import views

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'order-tracking', OrderTrackingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
     path('cart/', views.view_cart_page, name='view-cart-page'),  # HTML page
    path('api/cart/', views.get_cart_items_api, name='cart-items-api'),  # API endpoint
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    path('cart/delete/<int:pk>/', views.delete_cart_item, name='delete_cart_item'),

    path('api/create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('api/verify-payment/', views.verify_payment, name='verify_payment'),
] 
