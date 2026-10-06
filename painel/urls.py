from django.urls import path

from . import views

urlpatterns = [
    path("", views.cardapio_semana, name="painel_cardapio"),
    path("cardapio/<str:data>/", views.linha_cardapio, name="painel_linha_cardapio"),
    path("confirmados/", views.confirmados, name="painel_confirmados"),
    path("avaliacoes/", views.avaliacoes, name="painel_avaliacoes"),
    path("importar/", views.importar, name="painel_importar"),
]
