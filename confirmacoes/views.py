from datetime import date, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Confirmacao


@login_required
@require_POST
def alternar(request, data: str):
    """
    Toggle de presença. POST puro na Sprint 1; na Sprint 2 vira hx-post devolvendo
    só o parcial _botao_confirmar.html (ADR-0004). A regra de negócio NÃO muda.
    """
    data_obj = date.fromisoformat(data)
    if not Confirmacao.pode_alterar_agora(data_obj):
        return HttpResponseForbidden("Passou do horário de corte para este dia.")

    Confirmacao.alternar(request.user, data_obj)
    return redirect("cardapio_dia", data=data)


@staff_member_required
def dashboard(request):
    """
    Painel da produção: confirmados de hoje + últimos 7 dias pra comparar.
    staff_member_required = só quem tem 'acesso ao admin' (a cozinha/diretoria) entra.
    """
    hoje = timezone.localdate()
    dias = [hoje - timedelta(days=i) for i in range(6, -1, -1)]  # 6 dias atrás … hoje
    historico = [{"data": d, "total": Confirmacao.total_do_dia(d), "e_hoje": d == hoje} for d in dias]
    maximo = max((h["total"] for h in historico), default=0) or 1  # evita divisão por zero na barra
    return render(
        request,
        "confirmacoes/dashboard.html",
        {"hoje": hoje, "total_hoje": Confirmacao.total_do_dia(hoje), "historico": historico, "maximo": maximo},
    )
