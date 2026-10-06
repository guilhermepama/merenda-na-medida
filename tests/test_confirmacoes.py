"""Toggle de presença — a funcionalidade central do produto (ADR-0010 item 2)."""
from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone

from confirmacoes.models import Confirmacao


def test_primeiro_toggle_cria_confirmado(client, usuario, cardapio_amanha, amanha):
    client.force_login(usuario)
    resp = client.post(reverse("confirmacao_alternar", args=[amanha.isoformat()]))
    assert resp.status_code == 302
    assert Confirmacao.objects.get(usuario=usuario, data=amanha).confirmado is True


def test_segundo_toggle_inverte_sem_duplicar(client, usuario, cardapio_amanha, amanha):
    client.force_login(usuario)
    url = reverse("confirmacao_alternar", args=[amanha.isoformat()])
    client.post(url)
    client.post(url)
    assert Confirmacao.objects.filter(usuario=usuario, data=amanha).count() == 1
    assert Confirmacao.objects.get(usuario=usuario, data=amanha).confirmado is False


def test_toggle_em_dia_passado_da_403(client, usuario):
    client.force_login(usuario)
    ontem = timezone.localdate() - timedelta(days=1)
    resp = client.post(reverse("confirmacao_alternar", args=[ontem.isoformat()]))
    assert resp.status_code == 403
    assert not Confirmacao.objects.filter(usuario=usuario, data=ontem).exists()


def test_toggle_exige_login(client, amanha):
    resp = client.post(reverse("confirmacao_alternar", args=[amanha.isoformat()]))
    assert resp.status_code == 302 and "/entrar/" in resp.url


def test_toggle_so_aceita_post(client, usuario, amanha):
    client.force_login(usuario)
    resp = client.get(reverse("confirmacao_alternar", args=[amanha.isoformat()]))
    assert resp.status_code == 405


def test_banco_impede_duas_confirmacoes_no_mesmo_dia(usuario, amanha):
    Confirmacao.objects.create(usuario=usuario, data=amanha)
    with pytest.raises(IntegrityError):
        Confirmacao.objects.create(usuario=usuario, data=amanha)
