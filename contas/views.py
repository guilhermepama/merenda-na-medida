from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import CadastroForm


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
