from django.contrib import admin

from .models import Avaliacao


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("data", "usuario", "nota", "repetiria", "comentario")
    list_filter = ("data", "nota", "repetiria")
    date_hierarchy = "data"
