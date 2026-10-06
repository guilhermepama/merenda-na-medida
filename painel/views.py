"""
Painel da cozinha (ADR-0012): as quatro tarefas da cozinha, sem passar pelo /admin/.
O /admin/ do Django continua existindo — para a equipe técnica, não para a cozinha.
"""
from datetime import date, timedelta

from django.contrib import messages
from django.db.models import Count
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from avaliacoes.models import Avaliacao
from cardapio.importacao import ErroImportacao, importar_csv, ler_texto
from cardapio.models import Cardapio
from confirmacoes.models import Confirmacao

from .permissoes import apenas_cozinha

DIAS_COM_JANTAR = 5  # segunda a sexta — o cardápio da Prefeitura só tem dias úteis
TAMANHO_MAXIMO_CSV = 512 * 1024  # um mês de cardápio tem ~3 KB; 512 KB é folga de sobra


# ---------- utilitários ----------

def _data_da_url(texto: str) -> date:
    """Data vinda do caminho da URL; data inválida vira 404 (e não erro 500)."""
    try:
        return date.fromisoformat(texto)
    except ValueError:
        raise Http404("Data inválida")


def _data_do_get(request, nome: str) -> date:
    """?data=AAAA-MM-DD opcional; ausente ou inválida = hoje."""
    try:
        return date.fromisoformat(request.GET.get(nome, ""))
    except ValueError:
        return timezone.localdate()


def _navegacao(dia: date, rota: str) -> dict:
    """Contexto do parcial _navegar_dia.html."""
    return {"dia": dia, "anterior": dia - timedelta(days=1), "proximo": dia + timedelta(days=1), "rota": rota}


def _e_htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true"


def _linha(dia: date, cardapio, total: int, editando: bool) -> dict:
    """Tudo que o parcial _linha_cardapio.html precisa para desenhar um dia."""
    return {
        "data": dia,
        "cardapio": cardapio,
        "total": total,
        "e_hoje": dia == timezone.localdate(),
        "editando": editando,
    }


# ---------- 1. cardápio da semana (edição inline) ----------

@apenas_cozinha
def cardapio_semana(request):
    """Segunda a sexta, um dia por linha, com o total de confirmados ao lado."""
    referencia = _data_do_get(request, "inicio")
    segunda = referencia - timedelta(days=referencia.weekday())
    dias = [segunda + timedelta(days=i) for i in range(DIAS_COM_JANTAR)]

    cardapios = {c.data: c for c in Cardapio.objects.filter(data__in=dias)}
    # GROUP BY data → {data: total}. Uma query para a semana inteira, não uma por dia.
    totais = dict(
        Confirmacao.objects.filter(data__in=dias, confirmado=True)
        .values_list("data")
        .annotate(n=Count("id"))
    )
    editar = request.GET.get("editar")  # fallback sem JS: ?editar=AAAA-MM-DD abre o formulário

    linhas = [_linha(d, cardapios.get(d), totais.get(d, 0), editar == d.isoformat()) for d in dias]
    return render(request, "painel/cardapio.html", {
        "linhas": linhas,
        "segunda": segunda,
        "sexta": dias[-1],
        "semana_anterior": segunda - timedelta(days=7),
        "proxima_semana": segunda + timedelta(days=7),
        "e_semana_atual": segunda <= timezone.localdate() < segunda + timedelta(days=7),
    })


@apenas_cozinha
def linha_cardapio(request, data: str):
    """
    Uma linha da semana, trocada no lugar pelo HTMX (ADR-0004):
    - GET            → linha em modo leitura (botão 'Cancelar')
    - GET ?editar=1  → linha em modo edição (botão 'Editar')
    - POST           → salva; descrição vazia = dia sem jantar (apaga o cardápio)
    Sem HTMX, o POST faz redirect para a semana — o painel funciona com JS desligado.
    """
    dia = _data_da_url(data)

    if request.method == "POST":
        descricao = request.POST.get("descricao", "").strip()
        if descricao:
            Cardapio.objects.update_or_create(data=dia, defaults={"descricao": descricao})
        else:
            Cardapio.objects.filter(data=dia).delete()
        if not _e_htmx(request):
            messages.success(request, f"Cardápio de {dia:%d/%m} salvo.")
            return redirect(f"{reverse('painel_cardapio')}?inicio={dia.isoformat()}")

    editando = request.method == "GET" and "editar" in request.GET
    linha = _linha(dia, Cardapio.objects.filter(data=dia).first(), Confirmacao.total_do_dia(dia), editando)
    return render(request, "painel/_linha_cardapio.html", {"l": linha})


# ---------- 2. confirmados do dia ----------

@apenas_cozinha
def confirmados(request):
    """Quem vai jantar no dia (nomes) — a lista que a cozinha imprime ou confere na porta."""
    dia = _data_do_get(request, "data")
    lista = (
        Confirmacao.objects.filter(data=dia, confirmado=True)
        .select_related("usuario")  # 1 query com JOIN, em vez de 1 por nome
        .order_by("usuario__first_name", "usuario__username")
    )
    return render(request, "painel/confirmados.html", {
        **_navegacao(dia, "painel_confirmados"),
        "cardapio": Cardapio.objects.filter(data=dia).first(),
        "confirmacoes": lista,
        "cancelaram": Confirmacao.objects.filter(data=dia, confirmado=False).count(),
    })


# ---------- 3. avaliações (anônimas) ----------

@apenas_cozinha
def avaliacoes(request):
    """
    Notas e comentários do dia, SEM o nome de quem avaliou: se a cozinha vê quem
    deu 1 estrela, o aluno para de avaliar com sinceridade (ADR-0012).
    """
    dia = _data_do_get(request, "data")
    do_dia = Avaliacao.objects.filter(data=dia)
    por_nota = dict(do_dia.values_list("nota").annotate(n=Count("id")))
    resumo = Avaliacao.resumo_do_dia(dia)
    maior = max(por_nota.values(), default=0) or 1  # evita divisão por zero na barra

    return render(request, "painel/avaliacoes.html", {
        **_navegacao(dia, "painel_avaliacoes"),
        "cardapio": Cardapio.objects.filter(data=dia).first(),
        "resumo": resumo,
        "confirmados": Confirmacao.total_do_dia(dia),
        "distribuicao": [{"nota": n, "total": por_nota.get(n, 0)} for n in range(5, 0, -1)],
        "maior": maior,
        # .values() só com os campos exibidos — o usuário nem sai do banco
        "comentarios": [
            {**c, "estrelas": "★" * c["nota"]}
            for c in do_dia.exclude(comentario="").order_by("-atualizado_em").values("nota", "repetiria", "comentario")
        ],
    })


# ---------- 4. importar o CSV do mês ----------

@apenas_cozinha
def importar(request):
    """Upload do CSV mensal. Mesma regra do comando importar_cardapio (cardapio/importacao.py)."""
    if request.method == "POST":
        arquivo = request.FILES.get("arquivo")
        try:
            if not arquivo:
                raise ErroImportacao("Escolha um arquivo .csv.")
            if not arquivo.name.lower().endswith(".csv"):
                raise ErroImportacao("O arquivo precisa ser .csv (no Excel: Salvar como → CSV UTF-8).")
            if arquivo.size > TAMANHO_MAXIMO_CSV:
                raise ErroImportacao("Arquivo grande demais para um cardápio mensal.")
            r = importar_csv(ler_texto(arquivo.read()))
        except ErroImportacao as erro:
            messages.error(request, f"Nada foi importado. {erro}")
        else:
            messages.success(
                request,
                f"Importado: {r['criados']} dias novos, {r['atualizados']} atualizados, {r['feriados']} feriados.",
            )
            return redirect("painel_cardapio")
    return render(request, "painel/importar.html")
