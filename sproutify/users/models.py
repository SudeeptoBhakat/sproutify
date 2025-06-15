from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings


# Gender Choices
GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    short_intro = models.TextField(blank=True, null=True)

    # Address Fields
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    pin_code = models.CharField(max_length=10)

    # Django Permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    def __str__(self):
        return f"{self.email}"



# PRODUCT MODEL
from django.db import models
from django.utils.text import slugify
from datetime import datetime

def upload_product_image(instance, filename):
    ext = filename.split('.')[-1]
    name = instance.name.replace(" ", "_")  # sanitize name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{name}-{timestamp}.{ext}"
    return f"products/{filename}"

CATEGORY_CHOICES = [
    ('indoor', 'Indoor Plant'),
    ('outdoor', 'Outdoor Plant'),
    ('flowering', 'Flowering Plant'),
    ('succulent', 'Succulent'),
    ('herb', 'Herbal Plant'),
    ('bonsai', 'Bonsai'),
    ('fruit', 'Fruit Plant'),
    ('other', 'Other'),
]

AVAILABILITY_STATUS = [
    ('in_stock', 'In Stock'),
    ('out_of_stock', 'Out of Stock'),
    ('preorder', 'Preorder'),
]

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField()
    care_instructions = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_STATUS, default='in_stock')

    image = models.ImageField(upload_to=upload_product_image, blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    height_cm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    pot_size = models.CharField(max_length=50, blank=True, null=True)
    climate = models.CharField(max_length=100, blank=True, null=True)
    sunlight = models.CharField(max_length=100, blank=True, null=True)
    water_frequency = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# PRODUCT REVIEW MODEL
class ProductReview(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'customer')  # Prevent multiple reviews by same customer
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.first_name} - {self.product.name} - {self.rating}★"
