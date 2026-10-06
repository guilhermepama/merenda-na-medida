"""Painel da cozinha (ADR-0012): acesso, edição inline, listas e upload do CSV."""
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from avaliacoes.models import Avaliacao
from cardapio.models import Cardapio
from confirmacoes.models import Confirmacao

HTMX = {"HTTP_HX_REQUEST": "true"}


# ---------- acesso ----------

@pytest.mark.parametrize("rota", ["painel_cardapio", "painel_confirmados", "painel_avaliacoes", "painel_importar"])
def test_painel_so_para_cozinha(client, usuario, cozinha, rota):
    url = reverse(rota)
    assert client.get(url).status_code == 302          # anônimo → login do site
    client.force_login(usuario)
    assert client.get(url).status_code == 403          # aluno → proibido, sem loop de login
    client.force_login(cozinha)
    assert client.get(url).status_code == 200


def test_anonimo_vai_para_login_do_site_e_nao_do_admin(client):
    resp = client.get(reverse("painel_cardapio"))
    assert resp.url.startswith(reverse("login"))


def test_aluno_nao_edita_cardapio(client, usuario, amanha):
    client.force_login(usuario)
    resp = client.post(reverse("painel_linha_cardapio", args=[amanha.isoformat()]), {"descricao": "hackeado"})
    assert resp.status_code == 403
    assert not Cardapio.objects.exists()


# ---------- cardápio da semana ----------

def test_semana_tem_segunda_a_sexta_com_totais(client, cozinha, usuario):
    hoje = timezone.localdate()
    segunda = hoje - timedelta(days=hoje.weekday())
    Confirmacao.objects.create(usuario=usuario, data=segunda, confirmado=True)
    client.force_login(cozinha)
    linhas = client.get(reverse("painel_cardapio")).context["linhas"]
    assert [l["data"].weekday() for l in linhas] == [0, 1, 2, 3, 4]
    assert linhas[0]["total"] == 1


def test_htmx_abre_edicao_e_salva_so_a_linha(client, cozinha, amanha):
    client.force_login(cozinha)
    url = reverse("painel_linha_cardapio", args=[amanha.isoformat()])

    form = client.get(url + "?editar=1", **HTMX)
    assert b"<textarea" in form.content and b"<html" not in form.content  # parcial, não a página

    resp = client.post(url, {"descricao": "  Arroz, feijão, frango  "}, **HTMX)
    assert b"<html" not in resp.content and b"Arroz, feij" in resp.content
    assert Cardapio.objects.get(data=amanha).descricao == "Arroz, feijão, frango"  # strip aplicado


def test_descricao_vazia_apaga_o_cardapio(client, cozinha, cardapio_amanha, amanha):
    client.force_login(cozinha)
    client.post(reverse("painel_linha_cardapio", args=[amanha.isoformat()]), {"descricao": ""}, **HTMX)
    assert not Cardapio.objects.filter(data=amanha).exists()


def test_sem_htmx_salva_e_redireciona(client, cozinha, amanha):
    client.force_login(cozinha)
    resp = client.post(reverse("painel_linha_cardapio", args=[amanha.isoformat()]), {"descricao": "Sopa"})
    assert resp.status_code == 302 and reverse("painel_cardapio") in resp.url
    assert Cardapio.objects.get(data=amanha).descricao == "Sopa"


def test_data_invalida_na_url_e_404(client, cozinha):
    client.force_login(cozinha)
    assert client.get(reverse("painel_linha_cardapio", args=["2026-13-45"])).status_code == 404


# ---------- confirmados ----------

def test_confirmados_lista_so_quem_vai(client, cozinha, usuario, amanha):
    outro = get_user_model().objects.create_user(username="bia", password="x-y-z-123", first_name="Bia")
    Confirmacao.objects.create(usuario=usuario, data=amanha, confirmado=True)
    Confirmacao.objects.create(usuario=outro, data=amanha, confirmado=False)
    client.force_login(cozinha)
    resp = client.get(reverse("painel_confirmados") + f"?data={amanha.isoformat()}")
    assert [c.usuario.username for c in resp.context["confirmacoes"]] == ["ana"]
    assert resp.context["cancelaram"] == 1


# ---------- avaliações ----------

def test_avaliacoes_sao_anonimas_para_a_cozinha(client, cozinha, usuario, cardapio_amanha, amanha):
    Avaliacao.objects.create(usuario=usuario, data=amanha, nota=2, comentario="Arroz frio")
    client.force_login(cozinha)
    resp = client.get(reverse("painel_avaliacoes") + f"?data={amanha.isoformat()}")
    corpo = resp.content.decode()
    assert "Arroz frio" in corpo
    assert "Ana" not in corpo.split("</nav>", 1)[1]  # nome do aluno não aparece (fora da navbar da cozinha)
    assert "usuario" not in resp.context["comentarios"][0]


# ---------- importar CSV ----------

def _csv(texto: str, nome="cardapio.csv", bom=False) -> SimpleUploadedFile:
    dados = ("﻿" + texto if bom else texto).encode("utf-8")
    return SimpleUploadedFile(nome, dados, content_type="text/csv")


def test_upload_importa_csv_salvo_pelo_excel(client, cozinha):
    """Excel no Windows grava BOM no início — tem que funcionar mesmo assim."""
    client.force_login(cozinha)
    texto = 'data,descricao\n2026-10-05,"Arroz, Feijão"\n2026-10-12,FERIADO\n'
    resp = client.post(reverse("painel_importar"), {"arquivo": _csv(texto, bom=True)})
    assert resp.status_code == 302
    assert Cardapio.objects.count() == 1


def test_upload_com_linha_errada_nao_grava_nada(client, cozinha):
    client.force_login(cozinha)
    texto = "data,descricao\n2026-10-05,Arroz\n05/10/2026,Feijão\n"  # 2ª linha com data no formato errado
    resp = client.post(reverse("painel_importar"), {"arquivo": _csv(texto)}, follow=True)
    assert not Cardapio.objects.exists()  # transação: a 1ª linha também foi desfeita
    assert "Linha 3" in resp.content.decode()


def test_upload_recusa_arquivo_que_nao_e_csv(client, cozinha):
    client.force_login(cozinha)
    resp = client.post(reverse("painel_importar"), {"arquivo": _csv("data,descricao\n", nome="cardapio.xlsx")})
    assert resp.status_code == 200 and "precisa ser .csv" in resp.content.decode()
