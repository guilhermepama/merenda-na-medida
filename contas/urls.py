from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("cadastro/", views.cadastro, name="cadastro"),
    path("preferencias/", views.preferencias, name="preferencias"),
    path("telegram/", views.telegram, name="telegram"),
    path("entrar/", auth_views.LoginView.as_view(template_name="contas/login.html"), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
]
