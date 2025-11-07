# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Регистрируем CustomUser в админке на базе стандартного UserAdmin,
    добавляя поля phone и birth_city.
    """
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'birth_city')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone', 'birth_city')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')
    search_fields = ('username', 'email', 'phone')
