from django.urls import path

from . import views

urlpatterns = [
    path("", views.hoje, name="home"),
    path("cardapio/semana/", views.semana, name="cardapio_semana"),
    path("cardapio/<str:data>/", views.dia, name="cardapio_dia"),
]
