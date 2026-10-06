from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cardapio.models import Cardapio

from .forms import AvaliacaoForm
from .models import Avaliacao
from .regras import pode_avaliar


def pode_avaliar_agora(data_jantar: date) -> bool:
    return pode_avaliar(data_jantar, timezone.localtime(), settings.HORARIO_JANTAR)


@login_required
def avaliar(request, data: str):
    """Nota + 'repetiria' do jantar de uma data. Cria ou edita a avaliação do usuário (uma por dia)."""
    data_obj = date.fromisoformat(data)
    cardapio = get_object_or_404(Cardapio, data=data_obj)
    if not pode_avaliar_agora(data_obj):
        return HttpResponseForbidden("Este jantar ainda não foi servido.")

    existente = Avaliacao.objects.filter(usuario=request.user, data=data_obj).first()
    form = AvaliacaoForm(request.POST or None, instance=existente, initial=None if existente else {"nota": 4})
    if request.method == "POST" and form.is_valid():
        avaliacao = form.save(commit=False)
        avaliacao.usuario, avaliacao.data = request.user, data_obj
        avaliacao.save()
        messages.success(request, "Avaliação registrada. Obrigado!")
        return redirect("cardapio_dia", data=data)

    return render(request, "avaliacoes/avaliar.html", {"form": form, "cardapio": cardapio, "data": data_obj, "existente": existente})
