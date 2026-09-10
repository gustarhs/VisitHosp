from datetime import datetime

SLOTS_PADRAO = [
    ("09:00", "09:30"),
    ("09:30", "10:00"),
    ("10:00", "10:30"),
    ("10:30", "11:00"),
    ("14:00", "14:30"),
    ("14:30", "15:00"),
    ("15:00", "15:30"),
    ("15:30", "16:00"),
]
CAPACIDADE_MAXIMA_POR_HORARIO = 3


def parse_data_opcional(valor, nome_campo):
    if not valor:
        return None
    return parse_data_obrigatoria(valor, nome_campo)


def parse_data_obrigatoria(valor, nome_campo):
    try:
        return datetime.fromisoformat(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nome_campo} deve estar no formato ISO 8601 (ex: 2026-09-01T14:00:00)")