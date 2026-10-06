from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    # autenticação (ADR-0005): o bot troca usuário/senha por um par de tokens
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # recursos
    path("cardapio/hoje/", views.CardapioDoDia.as_view(), name="api_cardapio_hoje"),
    path("cardapio/<str:data>/", views.CardapioDoDia.as_view(), name="api_cardapio_data"),
    path("confirmacoes/", views.Confirmar.as_view(), name="api_confirmar"),
    path("vincular/", views.Vincular.as_view(), name="api_vincular"),
    path("usuarios/<str:telegram_id>/", views.Quem.as_view(), name="api_quem"),
    # documentação
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
]
