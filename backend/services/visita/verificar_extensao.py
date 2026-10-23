from repositories.visita_repository import VisitaRepository
from services.visita._helpers import parse_data_obrigatoria

def verificar_extensao(id_leito, horario_agendado_str):
    """sp_verificar_slot_extensao: valida o horário e delega para a Repository."""
    horario_agendado = parse_data_obrigatoria(horario_agendado_str, "horario_agendado")
    return VisitaRepository.sp_verificar_slot_extensao(id_leito, horario_agendado)