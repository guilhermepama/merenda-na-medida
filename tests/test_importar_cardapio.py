"""Carga mensal via CSV é idempotente e respeita feriados."""
from io import StringIO

from django.core.management import call_command

from cardapio.models import Cardapio

CSV = """data,descricao
2026-10-05,"Arroz, Feijão, Carne Moída"
2026-10-12,FERIADO
"""


def test_importa_e_pula_feriado(db, tmp_path):
    arq = tmp_path / "c.csv"
    arq.write_text(CSV, encoding="utf-8")
    saida = StringIO()
    call_command("importar_cardapio", str(arq), stdout=saida)
    assert Cardapio.objects.count() == 1
    assert "1 criados" in saida.getvalue() and "1 feriados" in saida.getvalue()


def test_reimportar_atualiza_sem_duplicar(db, tmp_path):
    arq = tmp_path / "c.csv"
    arq.write_text(CSV, encoding="utf-8")
    call_command("importar_cardapio", str(arq), stdout=StringIO())
    arq.write_text(CSV.replace("Carne Moída", "Frango"), encoding="utf-8")
    saida = StringIO()
    call_command("importar_cardapio", str(arq), stdout=saida)
    assert Cardapio.objects.count() == 1
    assert "Frango" in Cardapio.objects.get().descricao
    assert "1 atualizados" in saida.getvalue()
