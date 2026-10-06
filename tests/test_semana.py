"""Lista da semana com toggle por dia e navegação entre semanas."""
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from cardapio.models import Cardapio
from confirmacoes.models import Confirmacao


def test_semana_mostra_toggle_so_para_dias_com_cardapio(client, usuario, cardapio_amanha, amanha):
    client.force_login(usuario)
    html = client.get(reverse("cardapio_semana"), {"inicio": amanha.isoformat()}).content.decode()
    assert f'id="semana-{amanha.isoformat()}"' in html
    assert html.count("Vou jantar") == 1  # só amanhã tem cardápio


def test_semana_deslogado_nao_tem_toggle(client, cardapio_amanha, amanha):
    html = client.get(reverse("cardapio_semana"), {"inicio": amanha.isoformat()}).content.decode()
    assert "Vou jantar" not in html


def test_toggle_origem_semana_devolve_botao_compacto(client, usuario, cardapio_amanha, amanha):
    client.force_login(usuario)
    url = reverse("confirmacao_alternar", args=[amanha.isoformat()]) + "?origem=semana"
    resp = client.post(url, HTTP_HX_REQUEST="true")
    html = resp.content.decode()
    assert resp.status_code == 200
    assert f'id="semana-{amanha.isoformat()}"' in html and "card-confirmacao" not in html
    assert "✅ Vou" in html
    assert Confirmacao.objects.get(usuario=usuario, data=amanha).confirmado is True


def test_navegacao_entre_semanas(client, db):
    hoje = timezone.localdate()
    resp = client.get(reverse("cardapio_semana"), {"inicio": (hoje + timedelta(days=14)).isoformat()})
    assert resp.status_code == 200
    segunda = resp.context["semana"][0]["data"]
    assert segunda.weekday() == 0 and segunda > hoje


def test_inicio_invalido_cai_na_semana_atual(client, db):
    resp = client.get(reverse("cardapio_semana"), {"inicio": "banana"})
    assert resp.status_code == 200 and any(d["e_hoje"] for d in resp.context["semana"])
