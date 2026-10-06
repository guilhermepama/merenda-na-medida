from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("cardapio.urls")),       # / , /cardapio/...
    path("", include("confirmacoes.urls")),   # /confirmar/..., /producao/
    path("", include("contas.urls")),         # /cadastro/, /entrar/, /sair/
]
