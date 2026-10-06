from datetime import date, datetime, time

from avaliacoes.regras import pode_avaliar

JANTAR = time(20, 40)
HOJE = date(2026, 10, 6)


def test_hoje_antes_do_jantar_nao_pode():
    assert pode_avaliar(HOJE, datetime(2026, 10, 6, 20, 39), JANTAR) is False


def test_hoje_depois_do_jantar_pode():
    assert pode_avaliar(HOJE, datetime(2026, 10, 6, 20, 40), JANTAR) is True


def test_ontem_pode():
    assert pode_avaliar(date(2026, 10, 5), datetime(2026, 10, 6, 8, 0), JANTAR) is True


def test_amanha_nao_pode():
    assert pode_avaliar(date(2026, 10, 7), datetime(2026, 10, 6, 23, 0), JANTAR) is False
