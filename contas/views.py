from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CadastroForm, PreferenciasForm
from .models import CodigoVinculo


def cadastro(request):
    """Cria a conta e já loga — sem tela intermediária."""
    if request.user.is_authenticated:
        return redirect("home")
    form = CadastroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, "Conta criada. Bem-vindo!")
        return redirect("home")
    return render(request, "contas/cadastro.html", {"form": form})


@login_required
def preferencias(request):
    """Nome, e-mail e canal de notificação. Alpine só mostra/oculta o aviso do Telegram (ADR-0004)."""
    form = PreferenciasForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Preferências salvas.")
        return redirect("preferencias")
    return render(request, "contas/preferencias.html", {"form": form})


@login_required
def telegram(request):
    """Gera o código de vínculo e mostra o passo a passo. POST = gerar outro; ?desvincular=1 = remover."""
    if request.method == "POST":
        if request.POST.get("acao") == "desvincular":
            request.user.telegram_id = None
            request.user.save(update_fields=["telegram_id"])
            messages.info(request, "Telegram desvinculado.")
        else:
            CodigoVinculo.gerar(request.user)
        return redirect("telegram")

    codigo = request.user.codigos_vinculo.filter(usado_em__isnull=True).order_by("-criado_em").first()
    if codigo and not codigo.valido():
        codigo = None
    return render(request, "contas/telegram.html", {"codigo": codigo})
