from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    # Fase 1 — login/logout usam as views prontas do Django; só o template é nosso
    path("entrar/", auth_views.LoginView.as_view(template_name="contas/login.html"), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    # Fase 1: path("", include("cardapio.urls")), include("confirmacoes.urls"), include("contas.urls")
]
