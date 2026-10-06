from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "first_name", "email", "telegram_id", "notificacao")
    fieldsets = UserAdmin.fieldsets + (
        ("Merenda", {"fields": ("telegram_id", "notificacao")}),
    )
