from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product
from django.forms import TextInput, Textarea
from django import forms
from django.contrib import admin


class UserAdminConfig(UserAdmin):
    model = CustomUser
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    list_filter = ('is_active', 'is_staff', 'gender')
    ordering = ('-date_joined',)
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': (
            'first_name', 'last_name', 'phone', 'gender', 'short_intro',
            'state', 'district', 'address_line1', 'street', 'pin_code'
        )}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'gender', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )

admin.site.register(CustomUser, UserAdminConfig)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'stock_quantity', 'availability', 'created_at']
    list_filter = ['category', 'availability']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
