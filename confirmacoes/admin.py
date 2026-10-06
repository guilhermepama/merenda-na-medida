from django.contrib import admin

from .models import Confirmacao


@admin.register(Confirmacao)
class ConfirmacaoAdmin(admin.ModelAdmin):
    list_display = ("data", "usuario", "confirmado", "atualizado_em")
    list_filter = ("data", "confirmado")
    date_hierarchy = "data"
