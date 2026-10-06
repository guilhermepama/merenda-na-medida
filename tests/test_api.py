"""API do bot: JWT, permissão exclusiva do bot, cardápio, confirmação e vínculo (ADR-0005)."""
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from confirmacoes.models import Confirmacao
from contas.models import CodigoVinculo


@pytest.fixture
def bot(db, settings):
    return get_user_model().objects.create_user(username=settings.BOT_USERNAME, password="segredo-do-bot-123")


@pytest.fixture
def api(client, bot):
    """Client já autenticado com o JWT do bot — o mesmo fluxo que o bot real faz."""
    resp = client.post(reverse("token"), {"username": bot.username, "password": "segredo-do-bot-123"})
    assert resp.status_code == 200 and "access" in resp.json()
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {resp.json()['access']}"
    return client


@pytest.fixture
def aluno_vinculado(usuario):
    usuario.telegram_id = "111222333"
    usuario.save()
    return usuario


def test_sem_token_401(client, db):
    assert client.get(reverse("api_cardapio_hoje")).status_code == 401


def test_aluno_com_jwt_nao_entra(client, usuario, cardapio_amanha, amanha):
    usuario.set_password("senha-forte-123"); usuario.save()
    tok = client.post(reverse("token"), {"username": usuario.username, "password": "senha-forte-123"}).json()["access"]
    resp = client.get(reverse("api_cardapio_data", args=[amanha.isoformat()]), HTTP_AUTHORIZATION=f"Bearer {tok}")
    assert resp.status_code == 403


def test_cardapio_por_data(api, cardapio_amanha, amanha):
    resp = api.get(reverse("api_cardapio_data", args=[amanha.isoformat()]))
    assert resp.status_code == 200
    assert resp.json() == {"data": amanha.isoformat(), "descricao": cardapio_amanha.descricao, "total_confirmados": 0}


def test_cardapio_inexistente_404(api, db, amanha):
    assert api.get(reverse("api_cardapio_data", args=[amanha.isoformat()])).status_code == 404


def test_confirmar_vou_e_nao_vou(api, aluno_vinculado, cardapio_amanha, amanha):
    resp = api.post(reverse("api_confirmar"), {"telegram_id": "111222333", "data": amanha.isoformat(), "confirmado": True}, content_type="application/json")
    assert resp.status_code == 200 and resp.json()["total_confirmados"] == 1
    resp = api.post(reverse("api_confirmar"), {"telegram_id": "111222333", "data": amanha.isoformat(), "confirmado": False}, content_type="application/json")
    assert resp.json() == {"data": amanha.isoformat(), "confirmado": False, "total_confirmados": 0}
    assert Confirmacao.objects.filter(usuario=aluno_vinculado).count() == 1


def test_confirmar_telegram_desconhecido_404(api, db, amanha):
    resp = api.post(reverse("api_confirmar"), {"telegram_id": "000", "data": amanha.isoformat(), "confirmado": True}, content_type="application/json")
    assert resp.status_code == 404


def test_confirmar_apos_corte_403(api, aluno_vinculado):
    ontem = (timezone.localdate() - timedelta(days=1)).isoformat()
    resp = api.post(reverse("api_confirmar"), {"telegram_id": "111222333", "data": ontem, "confirmado": True}, content_type="application/json")
    assert resp.status_code == 403


def test_vincular_com_codigo_valido(api, usuario):
    codigo = CodigoVinculo.gerar(usuario)
    resp = api.post(reverse("api_vincular"), {"telegram_id": "999", "codigo": codigo.codigo}, content_type="application/json")
    assert resp.status_code == 200 and resp.json()["nome"] == "Ana"
    usuario.refresh_from_db()
    assert usuario.telegram_id == "999"
    # uso único
    assert api.post(reverse("api_vincular"), {"telegram_id": "888", "codigo": codigo.codigo}, content_type="application/json").status_code == 400


def test_vincular_codigo_expirado(api, usuario):
    codigo = CodigoVinculo.gerar(usuario)
    CodigoVinculo.objects.filter(pk=codigo.pk).update(criado_em=timezone.now() - timedelta(minutes=11))
    resp = api.post(reverse("api_vincular"), {"telegram_id": "999", "codigo": codigo.codigo}, content_type="application/json")
    assert resp.status_code == 400


def test_quem(api, aluno_vinculado):
    assert api.get(reverse("api_quem", args=["111222333"])).json() == {"nome": "Ana", "notificacao": "site"}
    assert api.get(reverse("api_quem", args=["nao-existe"])).status_code == 404


def test_swagger_abre(client, db):
    assert client.get(reverse("swagger")).status_code == 200
    assert client.get(reverse("schema")).status_code == 200
