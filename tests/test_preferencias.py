from django.urls import reverse


def test_preferencias_exige_login(client, db):
    assert client.get(reverse("preferencias")).status_code == 302


def test_salvar_canal_de_notificacao(client, usuario):
    client.force_login(usuario)
    resp = client.post(reverse("preferencias"), {"first_name": "Ana", "email": "a@x.com", "notificacao": "ambos"})
    assert resp.status_code == 302
    usuario.refresh_from_db()
    assert usuario.notificacao == "ambos"


def test_pagina_tem_alpine(client, usuario):
    client.force_login(usuario)
    html = client.get(reverse("preferencias")).content.decode()
    assert 'x-data=' in html and 'x-show=' in html
