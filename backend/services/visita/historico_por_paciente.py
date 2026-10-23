from repositories.visita_repository import VisitaRepository
from services.visita._helpers import parse_data_opcional

def historico_por_paciente(id_paciente, data_inicio_str=None, data_fim_str=None):
    """sp_historico_visitas_paciente: valida datas opcionais e delega para a Repository."""
    data_inicio = parse_data_opcional(data_inicio_str, "data_inicio")
    data_fim = parse_data_opcional(data_fim_str, "data_fim")
    return VisitaRepository.sp_historico_visitas_paciente(id_paciente, data_inicio, data_fim)