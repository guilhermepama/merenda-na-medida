"""Página /telegram/: gera código, mostra, desvincula."""
from django.urls import reverse

from contas.models import CodigoVinculo


def test_gerar_codigo(client, usuario):
    client.force_login(usuario)
    assert client.post(reverse("telegram")).status_code == 302
    codigo = CodigoVinculo.objects.get(usuario=usuario)
    assert len(codigo.codigo) == 6 and codigo.valido()
    assert codigo.codigo in client.get(reverse("telegram")).content.decode()


def test_gerar_de_novo_invalida_o_anterior(client, usuario):
    client.force_login(usuario)
    client.post(reverse("telegram")); client.post(reverse("telegram"))
    assert CodigoVinculo.objects.filter(usuario=usuario, usado_em__isnull=True).count() == 1


def test_desvincular(client, usuario):
    usuario.telegram_id = "123"; usuario.save()
    client.force_login(usuario)
    client.post(reverse("telegram"), {"acao": "desvincular"})
    usuario.refresh_from_db()
    assert usuario.telegram_id is None


def test_robots(client):
    resp = client.get("/robots.txt")
    assert resp.status_code == 200 and b"Disallow: /api/" in resp.content
