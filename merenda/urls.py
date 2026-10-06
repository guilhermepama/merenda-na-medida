from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

def robots(_request):
    """SEO básico (S3): indexar o cardápio público, não as páginas de conta/admin/API."""
    return HttpResponse("User-agent: *\nDisallow: /admin/\nDisallow: /api/\nDisallow: /producao/\nDisallow: /preferencias/\n", content_type="text/plain")


urlpatterns = [
    path("robots.txt", robots),
    path("admin/", admin.site.urls),
    path("", include("cardapio.urls")),       # / , /cardapio/...
    path("", include("confirmacoes.urls")),   # /confirmar/..., /producao/
    path("", include("contas.urls")),         # /cadastro/, /entrar/, /sair/, /preferencias/
    path("", include("avaliacoes.urls")),     # /avaliar/<data>/
    path("api/", include("api.urls")),        # ADR-0005 — consumida pelo bot; docs em /api/docs/
]
