from django.urls import path
from .views import (
    ProductCreateView,
    ProductListView,
    index,
    product_detail_view,
    product_search,
    profile,
    user_register,
    validate_token,
    LoginView,
    UserProfileView,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('', index, name='index.html'),
    path('profile/', profile, name='profile.html'),
    path('user/register/', user_register, name='new-user-register'),
    path('api/login/', LoginView.as_view(), name='user-login'),
     path('api/validate-token/', validate_token, name='validate-token'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('api/', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
]


urlpatterns += [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path("api/products/search/", product_search, name="product-search"),
    path("product/<int:id>/", product_detail_view, name="product-detail"),
]