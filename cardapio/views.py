"""
Consulta do cardápio. Só leitura — quem escreve é o admin (S1.4).
"""
from datetime import date, timedelta

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from avaliacoes.models import Avaliacao
from avaliacoes.views import pode_avaliar_agora
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

    confirmacao = minha_avaliacao = None
    if request.user.is_authenticated:
        confirmacao = Confirmacao.objects.filter(usuario=request.user, data=data_obj).first()
        if cardapio:
            minha_avaliacao = Avaliacao.objects.filter(usuario=request.user, data=data_obj).first()

    contexto = {
        "data": data_obj,
        "cardapio": cardapio,
        "anterior": data_obj - timedelta(days=1),
        "proximo": data_obj + timedelta(days=1),
        "e_hoje": data_obj == timezone.localdate(),
        "confirmacao": confirmacao,
        "pode_alterar": Confirmacao.pode_alterar_agora(data_obj),
        "total_confirmados": Confirmacao.total_do_dia(data_obj),
        "pode_avaliar": pode_avaliar_agora(data_obj),
        "minha_avaliacao": minha_avaliacao,
        "resumo_avaliacao": Avaliacao.resumo_do_dia(data_obj) if cardapio else {"total": 0},
    }
    return render(request, "cardapio/dia.html", contexto)


def semana(request):
    """
    Segunda a domingo, com o cardápio de cada dia e — se logado — o toggle de presença
    por dia, pra planejar a semana inteira numa tela. ?inicio=YYYY-MM-DD navega entre semanas.
    """
    hoje_ = timezone.localdate()
    try:
        referencia = date.fromisoformat(request.GET.get("inicio", ""))
    except ValueError:
        referencia = hoje_
    segunda = referencia - timedelta(days=referencia.weekday())
    dias = [segunda + timedelta(days=i) for i in range(7)]

    cardapios = {c.data: c for c in Cardapio.objects.filter(data__in=dias)}
    confirmacoes = {}
    if request.user.is_authenticated:
        confirmacoes = {c.data: c for c in Confirmacao.objects.filter(usuario=request.user, data__in=dias)}

    semana_ = [
        {
            "data": d,
            "cardapio": cardapios.get(d),
            "e_hoje": d == hoje_,
            "confirmacao": confirmacoes.get(d),
            "pode_alterar": Confirmacao.pode_alterar_agora(d),
        }
        for d in dias
    ]
    return render(request, "cardapio/semana.html", {
        "semana": semana_,
        "semana_anterior": segunda - timedelta(days=7),
        "proxima_semana": segunda + timedelta(days=7),
    })
