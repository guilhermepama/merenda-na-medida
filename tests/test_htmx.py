"""Toggle via HTMX devolve só o card, sem redirect (ADR-0004)."""
from django.urls import reverse

from confirmacoes.models import Confirmacao


def test_toggle_htmx_devolve_parcial(client, usuario, cardapio_amanha, amanha):
    client.force_login(usuario)
    resp = client.post(reverse("confirmacao_alternar", args=[amanha.isoformat()]), HTTP_HX_REQUEST="true")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert 'id="card-confirmacao"' in html
    assert "<html" not in html                       # parcial, não página inteira
    assert "1</strong> pessoa confirmada" in html    # contagem já atualizada
    assert "cancelar" in html                         # botão já invertido
    assert Confirmacao.objects.get(usuario=usuario, data=amanha).confirmado is True


def test_toggle_sem_htmx_continua_redirecionando(client, usuario, cardapio_amanha, amanha):
    client.force_login(usuario)
    resp = client.post(reverse("confirmacao_alternar", args=[amanha.isoformat()]))
    assert resp.status_code == 302
