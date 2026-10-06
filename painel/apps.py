from django.apps import AppConfig


class PainelConfig(AppConfig):
    """Área da cozinha (ADR-0012). Sem models: é uma interface sobre cardapio/confirmacoes/avaliacoes."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "painel"
