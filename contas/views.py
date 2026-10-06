from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CadastroForm, PreferenciasForm


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
