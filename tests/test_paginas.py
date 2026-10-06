"""Smoke: as páginas principais abrem (ADR-0010, 'cada URL responde')."""
from django.urls import reverse


def test_home_redireciona_para_hoje(client, db):
    resp = client.get("/")
    assert resp.status_code == 302 and "/cardapio/" in resp.url


def test_dia_sem_cardapio_abre_vazio(client, db, amanha):
    resp = client.get(reverse("cardapio_dia", args=[amanha.isoformat()]))
    assert resp.status_code == 200
    assert "ainda não cadastrado" in resp.content.decode()


def test_dia_com_cardapio_mostra_descricao(client, cardapio_amanha, amanha):
    resp = client.get(reverse("cardapio_dia", args=[amanha.isoformat()]))
    assert "frango grelhado" in resp.content.decode()


def test_semana_abre(client, db):
    assert client.get(reverse("cardapio_semana")).status_code == 200


def test_cadastro_cria_e_loga(client, db):
    resp = client.post(reverse("cadastro"), {
        "username": "novo", "first_name": "Novo", "email": "n@x.com",
        "password1": "senha-forte-123", "password2": "senha-forte-123",
    })
    assert resp.status_code == 302
    assert client.get("/").wsgi_request.user.is_authenticated
