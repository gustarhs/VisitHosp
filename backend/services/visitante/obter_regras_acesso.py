from repositories.visitante_repository import VisitanteRepository

def obter_regras_acesso(id_visitante):
    """sp_obter_regras_acesso_por_papel: delega para a Repository."""
    return VisitanteRepository.sp_obter_regras_acesso_por_papel(id_visitante)