from repositories.visita_repository import VisitaRepository
from services.visita._helpers import parse_data_obrigatoria

def relatorio_auditoria(periodo_inicio_str, periodo_fim_str, id_leito=None):
    """sp_relatorio_auditoria_fluxo: valida o período obrigatório e delega para a Repository."""
    periodo_inicio = parse_data_obrigatoria(periodo_inicio_str, "periodo_inicio")
    periodo_fim = parse_data_obrigatoria(periodo_fim_str, "periodo_fim")
    return VisitaRepository.sp_relatorio_auditoria_fluxo(id_leito, periodo_inicio, periodo_fim)