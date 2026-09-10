from datetime import datetime
from repositories.leito_repository import LeitoRepository

def verificar_disponibilidade_slots(id_leito, data_visita_str):
    """Valida a entrada e delega a consulta de slots para a Repository (sp_verificar_disponibilidade_slots)."""
    try:
        data_visita = datetime.fromisoformat(data_visita_str).date()
    except (TypeError, ValueError):
        raise ValueError("data_visita deve estar no formato YYYY-MM-DD")

    return LeitoRepository.sp_verificar_disponibilidade_slots(id_leito, data_visita)