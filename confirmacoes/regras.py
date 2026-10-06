"""
Regras de negócio da confirmação de presença (ADR-0008).

Funções puras: recebem valores, devolvem valores, não tocam no banco.
Por isso são testáveis sem Django rodando — ver tests/test_regras.py.
Site e bot chamam a MESMA função; a regra existe em um lugar só.
"""
from datetime import date, datetime, time


def pode_alterar(data_jantar: date, agora: datetime, horario_corte: time) -> bool:
    """
    O aluno pode confirmar/cancelar o jantar de `data_jantar`?

    - Jantar de um dia futuro: sempre pode.
    - Jantar de hoje: só até o horário de corte (inclusive).
    - Jantar de um dia passado: nunca.
    """
    hoje = agora.date()
    if data_jantar > hoje:
        return True
    if data_jantar < hoje:
        return False
    return agora.time() <= horario_corte
