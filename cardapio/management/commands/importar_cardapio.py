"""
python manage.py importar_cardapio dados/cardapio-2026-10.csv

Carga mensal do cardápio a partir de CSV (data,descricao). Idempotente:
update_or_create por data — rodar duas vezes não duplica. 'FERIADO' pula o dia
(e remove um cardápio que exista nele, caso tenha virado feriado depois).
"""
import csv
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from cardapio.models import Cardapio


class Command(BaseCommand):
    help = "Importa/atualiza cardápios a partir de um CSV com colunas data,descricao"

    def add_arguments(self, parser):
        parser.add_argument("arquivo", type=Path)

    def handle(self, arquivo: Path, **opts):
        if not arquivo.exists():
            raise CommandError(f"Arquivo não encontrado: {arquivo}")

        criados = atualizados = feriados = 0
        with arquivo.open(encoding="utf-8", newline="") as f:
            leitor = csv.DictReader(f)
            if set(leitor.fieldnames or []) != {"data", "descricao"}:
                raise CommandError("CSV precisa ter exatamente as colunas: data,descricao")

            for linha in leitor:
                dia = date.fromisoformat(linha["data"].strip())
                descricao = linha["descricao"].strip()

                if descricao.upper() == "FERIADO":
                    Cardapio.objects.filter(data=dia).delete()
                    feriados += 1
                    continue

                _, criado = Cardapio.objects.update_or_create(
                    data=dia, defaults={"descricao": descricao}
                )
                if criado:
                    criados += 1
                else:
                    atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{criados} criados, {atualizados} atualizados, {feriados} feriados ignorados."
            )
        )
