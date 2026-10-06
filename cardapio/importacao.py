"""
Regra de importação do cardápio mensal (CSV data,descricao).

Uma função, duas portas de entrada: o management command `importar_cardapio`
(terminal) e o upload do painel da cozinha (ADR-0012). Assim a regra
(upsert por data, FERIADO apaga o dia) existe em um lugar só.
"""
import csv
from datetime import date

from django.db import transaction

from .models import Cardapio


class ErroImportacao(ValueError):
    """CSV inválido. A mensagem é pensada para a cozinha ler."""


def ler_texto(conteudo: bytes) -> str:
    """
    bytes do arquivo → texto. 'utf-8-sig' remove o BOM que o Excel do Windows
    põe no começo do CSV — sem isso a 1ª coluna vira '\\ufeffdata' e nada bate.
    """
    try:
        return conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ErroImportacao("O arquivo não está em UTF-8. No Excel, salve como 'CSV UTF-8'.")


@transaction.atomic
def importar_csv(texto: str) -> dict:
    """
    Importa o CSV e devolve {'criados', 'atualizados', 'feriados'}.
    transaction.atomic: se uma linha estiver errada, NADA é gravado —
    a cozinha corrige o arquivo e importa de novo, sem mês pela metade.
    """
    leitor = csv.DictReader(texto.splitlines())
    if set(leitor.fieldnames or []) != {"data", "descricao"}:
        raise ErroImportacao("O CSV precisa ter exatamente as colunas: data,descricao")

    resultado = {"criados": 0, "atualizados": 0, "feriados": 0}
    for numero, linha in enumerate(leitor, start=2):  # linha 1 é o cabeçalho
        try:
            dia = date.fromisoformat((linha["data"] or "").strip())
        except ValueError:
            raise ErroImportacao(f"Linha {numero}: data '{linha['data']}' inválida (use AAAA-MM-DD).")
        descricao = (linha["descricao"] or "").strip()

        if descricao.upper() == "FERIADO":
            Cardapio.objects.filter(data=dia).delete()
            resultado["feriados"] += 1
            continue
        if not descricao:
            raise ErroImportacao(f"Linha {numero}: descrição vazia (use FERIADO se não houver jantar).")

        _, criado = Cardapio.objects.update_or_create(data=dia, defaults={"descricao": descricao})
        resultado["criados" if criado else "atualizados"] += 1
    return resultado
