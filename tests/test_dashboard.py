"""Contagem agregada — o número que a cozinha usa (ADR-0010 item 3)."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from confirmacoes.models import Confirmacao


def test_total_do_dia_conta_so_confirmados(db, usuario):
    hoje = timezone.localdate()
    outros = [get_user_model().objects.create_user(username=f"u{i}", password="x-y-z-123") for i in range(3)]
    Confirmacao.objects.create(usuario=usuario, data=hoje, confirmado=True)
    Confirmacao.objects.create(usuario=outros[0], data=hoje, confirmado=True)
    Confirmacao.objects.create(usuario=outros[1], data=hoje, confirmado=False)  # cancelou
    assert Confirmacao.total_do_dia(hoje) == 2


def test_dashboard_exige_staff(client, usuario, cozinha):
    url = reverse("dashboard")
    client.force_login(usuario)
    assert client.get(url).status_code == 403  # aluno comum é barrado (ADR-0012)
    client.force_login(cozinha)
    assert client.get(url).status_code == 200


def test_dashboard_mostra_total_de_hoje(client, cozinha, usuario):
    Confirmacao.objects.create(usuario=usuario, data=timezone.localdate())
    client.force_login(cozinha)
    resp = client.get(reverse("dashboard"))
    assert resp.context["total_hoje"] == 1
