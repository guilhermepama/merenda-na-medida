"""
Testes da regra de corte — escritos ANTES da implementação (TDD, ADR-0010).
Não precisam de banco: a função é pura.
"""
from datetime import date, datetime, time

from confirmacoes.regras import pode_alterar

CORTE = time(16, 0)
HOJE = date(2026, 10, 6)


def test_antes_do_corte_pode():
    agora = datetime(2026, 10, 6, 15, 59)
    assert pode_alterar(HOJE, agora, CORTE) is True


def test_exatamente_no_corte_ainda_pode():
    agora = datetime(2026, 10, 6, 16, 0)
    assert pode_alterar(HOJE, agora, CORTE) is True


def test_depois_do_corte_nao_pode():
    agora = datetime(2026, 10, 6, 16, 1)
    assert pode_alterar(HOJE, agora, CORTE) is False


def test_dia_futuro_sempre_pode_mesmo_tarde():
    amanha = date(2026, 10, 7)
    agora = datetime(2026, 10, 6, 23, 30)
    assert pode_alterar(amanha, agora, CORTE) is True


def test_dia_passado_nunca_pode_mesmo_cedo():
    ontem = date(2026, 10, 5)
    agora = datetime(2026, 10, 6, 8, 0)
    assert pode_alterar(ontem, agora, CORTE) is False
