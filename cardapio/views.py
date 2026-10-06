"""
Consulta do cardápio. Só leitura — quem escreve é o admin (S1.4).
"""
from datetime import date, timedelta

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from confirmacoes.models import Confirmacao

from .models import Cardapio


def hoje(request):
    """/ → redireciona pro dia de hoje. Assim a URL do dia é sempre compartilhável."""
    return redirect("cardapio_dia", data=timezone.localdate().isoformat())


def dia(request, data: str):
    """
    Cardápio de UMA data (YYYY-MM-DD). Pode não existir cardápio cadastrado ainda —
    aí mostramos a página vazia com navegação, em vez de 404.
    """
    data_obj = date.fromisoformat(data)
    cardapio = Cardapio.objects.filter(data=data_obj).first()

    confirmacao = None
    if request.user.is_authenticated:
        confirmacao = Confirmacao.objects.filter(usuario=request.user, data=data_obj).first()

    contexto = {
        "data": data_obj,
        "cardapio": cardapio,
        "anterior": data_obj - timedelta(days=1),
        "proximo": data_obj + timedelta(days=1),
        "e_hoje": data_obj == timezone.localdate(),
        "confirmacao": confirmacao,
        "pode_alterar": Confirmacao.pode_alterar_agora(data_obj),
        "total_confirmados": Confirmacao.total_do_dia(data_obj),
    }
    return render(request, "cardapio/dia.html", contexto)


def semana(request):
    """Segunda a domingo da semana atual, com o cardápio de cada dia (ou vazio)."""
    hoje_ = timezone.localdate()
    segunda = hoje_ - timedelta(days=hoje_.weekday())
    dias = [segunda + timedelta(days=i) for i in range(7)]
    cardapios = {c.data: c for c in Cardapio.objects.filter(data__in=dias)}
    semana_ = [{"data": d, "cardapio": cardapios.get(d), "e_hoje": d == hoje_} for d in dias]
    return render(request, "cardapio/semana.html", {"semana": semana_})
