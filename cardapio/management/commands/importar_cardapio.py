"""
python manage.py importar_cardapio dados/cardapio-2026-10.csv

Carga mensal do cardápio a partir de CSV (data,descricao). Idempotente:
update_or_create por data — rodar duas vezes não duplica. 'FERIADO' pula o dia
(e remove um cardápio que exista nele, caso tenha virado feriado depois).
A regra mora em cardapio/importacao.py — o upload do painel usa a mesma função.
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from cardapio.importacao import ErroImportacao, importar_csv, ler_texto


class Command(BaseCommand):
    help = "Importa/atualiza cardápios a partir de um CSV com colunas data,descricao"

    def add_arguments(self, parser):
        parser.add_argument("arquivo", type=Path)

    def handle(self, arquivo: Path, **opts):
        if not arquivo.exists():
            raise CommandError(f"Arquivo não encontrado: {arquivo}")
        try:
            r = importar_csv(ler_texto(arquivo.read_bytes()))
        except ErroImportacao as erro:
            raise CommandError(str(erro))

        self.stdout.write(
            self.style.SUCCESS(
                f"{r['criados']} criados, {r['atualizados']} atualizados, {r['feriados']} feriados ignorados."
            )
        )
