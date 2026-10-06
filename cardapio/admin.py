from django.contrib import admin

from .models import Cardapio


@admin.register(Cardapio)
class CardapioAdmin(admin.ModelAdmin):
    """Sprint 1 (S1.4). Desde o ADR-0012 a cozinha usa o /painel/; o admin fica para a equipe técnica."""

    list_display = ("data", "resumo")
    list_filter = ("data",)
    date_hierarchy = "data"
    ordering = ("-data",)

    @admin.display(description="Cardápio")
    def resumo(self, obj):
        return obj.descricao[:60]
