from django.shortcuts import render
from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import UserSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import json
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateDestroyAPIView



# Create your views here.
def index(request):
    return render(request, 'index.html')

def profile(request):
    return render(request, 'profile.html')

class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Allow only admin to list or create

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Allow only admin to update/delete


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({"detail": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
def user_register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            phone = data.get("phone")
            password = data.get("password")
            first_name = data.get("first_name")

            if CustomUser.objects.filter(email=email).exists() or CustomUser.objects.filter(phone=phone).exists():
                return JsonResponse({"error": "Email already registered"}, status=400)

            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name="",
                phone=phone,
                gender='O',  # default value
                state="", district="", address_line1="", street="", pin_code=""
            )

            return JsonResponse({"message": "Registered successfully!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')

        try:
            if email:
                user = CustomUser.objects.get(email=email)
            elif phone:
                user = CustomUser.objects.get(phone=phone)
            else:
                return Response({'detail': 'Email or Phone is required'}, status=400)

            user = authenticate(request, email=user.email, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                from .serializers import UserSerializer
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data
                })
            else:
                return Response({'detail': 'Invalid credentials'}, status=401)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def validate_token(request):
    user = request.user
    return Response({
        "message": "Token is valid",
        "first_name": user.first_name,
        "email": user.email,
        "phone": user.phone
    })







# PRODUCT
from rest_framework import generics, permissions
from .models import Product
from .serializers import ProductSerializer

# Public access: View all products
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []  # No auth required

# Admin-only: Create a new product
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin/superuser
