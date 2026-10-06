"""Avaliação: uma por (usuario, data), resumo agregado por dia (ADR-0011)."""
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone

from avaliacoes.models import Avaliacao
from cardapio.models import Cardapio


def test_unique_por_usuario_e_dia(usuario):
    d = timezone.localdate()
    Avaliacao.objects.create(usuario=usuario, data=d, nota=3)
    with pytest.raises(IntegrityError):
        Avaliacao.objects.create(usuario=usuario, data=d, nota=5)


def test_resumo_do_dia(db, usuario):
    d = timezone.localdate()
    u2, u3 = (get_user_model().objects.create_user(username=f"u{i}", password="x-y-z-123") for i in (2, 3))
    Avaliacao.objects.create(usuario=usuario, data=d, nota=4, repetiria=True)
    Avaliacao.objects.create(usuario=u2, data=d, nota=2, repetiria=False)
    Avaliacao.objects.create(usuario=u3, data=d, nota=3, repetiria=True)
    assert Avaliacao.resumo_do_dia(d) == {"total": 3, "media": 3.0, "pct_repetiria": 67}


def test_resumo_sem_avaliacoes(db):
    assert Avaliacao.resumo_do_dia(timezone.localdate()) == {"total": 0, "media": None, "pct_repetiria": None}


def test_view_avaliar_ontem_cria_e_edita(client, usuario):
    ontem = timezone.localdate() - timedelta(days=1)
    Cardapio.objects.create(data=ontem, descricao="Feijoada")
    client.force_login(usuario)
    url = reverse("avaliar", args=[ontem.isoformat()])
    assert client.get(url).status_code == 200
    assert client.post(url, {"nota": 4, "repetiria": "on", "comentario": "boa"}).status_code == 302
    assert client.post(url, {"nota": 2, "comentario": "hoje não"}).status_code == 302
    assert Avaliacao.objects.filter(usuario=usuario, data=ontem).count() == 1
    assert Avaliacao.objects.get(usuario=usuario, data=ontem).nota == 2


def test_view_avaliar_amanha_da_403(client, usuario, cardapio_amanha, amanha):
    client.force_login(usuario)
    assert client.get(reverse("avaliar", args=[amanha.isoformat()])).status_code == 403


def test_dia_mostra_resumo(client, usuario):
    ontem = timezone.localdate() - timedelta(days=1)
    Cardapio.objects.create(data=ontem, descricao="Feijoada")
    Avaliacao.objects.create(usuario=usuario, data=ontem, nota=5, repetiria=True)
    html = client.get(reverse("cardapio_dia", args=[ontem.isoformat()])).content.decode()
    assert "★ 5,0" in html and "100% repetiriam" in html  # pt-BR: vírgula decimal
