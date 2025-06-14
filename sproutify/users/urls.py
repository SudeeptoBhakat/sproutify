from django.urls import path
from .views import (
    ProductCreateView,
    ProductListView,
    index,
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
]