from datetime import date, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from avaliacoes.models import Avaliacao

from .models import Confirmacao


@login_required
@require_POST
def alternar(request, data: str):
    """
    Toggle de presença (ADR-0004).
    - Com HTMX (header HX-Request): devolve só o parcial _card_confirmacao.html e o
      navegador troca o card no lugar — sem reload.
    - Sem HTMX (JS desligado): POST normal + redirect, como na Sprint 1.
    A regra de negócio é a mesma nos dois caminhos.
    """
    data_obj = date.fromisoformat(data)
    e_htmx = request.headers.get("HX-Request") == "true"

    if Confirmacao.pode_alterar_agora(data_obj):
        Confirmacao.alternar(request.user, data_obj)
    elif not e_htmx:
        return HttpResponseForbidden("Passou do horário de corte para este dia.")
    # via HTMX, mesmo fora do prazo devolvemos o card: ele já mostra "prazo encerrado"

    if not e_htmx:
        return redirect("cardapio_dia", data=data)  # fallback sem JS continua funcionando

    # ?origem=semana → botão compacto da lista; senão, o card da página do dia
    parcial = "_botao_semana.html" if request.GET.get("origem") == "semana" else "_card_confirmacao.html"
    return render(request, f"confirmacoes/{parcial}", {
        "data": data_obj,
        "confirmacao": Confirmacao.objects.filter(usuario=request.user, data=data_obj).first(),
        "pode_alterar": Confirmacao.pode_alterar_agora(data_obj),
        "total_confirmados": Confirmacao.total_do_dia(data_obj),
    })


@staff_member_required
def dashboard(request):
    """
    Painel da produção: confirmados de hoje + últimos 7 dias pra comparar.
    staff_member_required = só quem tem 'acesso ao admin' (a cozinha/diretoria) entra.
    """
    hoje = timezone.localdate()
    dias = [hoje - timedelta(days=i) for i in range(6, -1, -1)]  # 6 dias atrás … hoje
    historico = [
        {"data": d, "total": Confirmacao.total_do_dia(d), "e_hoje": d == hoje, "avaliacao": Avaliacao.resumo_do_dia(d)}
        for d in dias
    ]
    maximo = max((h["total"] for h in historico), default=0) or 1  # evita divisão por zero na barra
    return render(
        request,
        "confirmacoes/dashboard.html",
        {"hoje": hoje, "total_hoje": Confirmacao.total_do_dia(hoje), "historico": historico, "maximo": maximo},
    )
