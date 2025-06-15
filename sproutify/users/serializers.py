from rest_framework import serializers
from .models import CustomUser, Product, ProductReview

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = ('id', 'is_active', 'is_staff', 'date_joined', 'is_superuser', 'last_login')



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
