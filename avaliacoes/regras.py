"""Quando um jantar pode ser avaliado. Função pura, como em confirmacoes/regras.py."""
from datetime import date, datetime, time


def pode_avaliar(data_jantar: date, agora: datetime, horario_jantar: time) -> bool:
    """
    Só depois que o jantar foi servido:
    - dia passado: pode;
    - hoje: a partir do horário do jantar;
    - futuro: não.
    """
    hoje = agora.date()
    if data_jantar < hoje:
        return True
    if data_jantar > hoje:
        return False
    return agora.time() >= horario_jantar
