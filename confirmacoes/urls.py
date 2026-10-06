from django.urls import path

from . import views

urlpatterns = [
    path("confirmar/<str:data>/", views.alternar, name="confirmacao_alternar"),
    path("producao/", views.dashboard, name="dashboard"),
]
