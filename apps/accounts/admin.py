from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("cpf", "full_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("cpf", "full_name", "email")
    ordering = ("full_name",)
    fieldsets = (
        (None, {"fields": ("cpf", "password")}),
        ("Dados Pessoais", {"fields": ("full_name", "email", "phone")}),
        ("Perfil", {"fields": ("role", "clinic")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("cpf", "full_name", "role", "password1", "password2"),
        }),
    )
