from repositories.visitante_repository import VisitanteRepository

def listar_pendentes():
    """sp_listar_cadastros_pendentes: delega para a Repository."""
    return VisitanteRepository.sp_listar_cadastros_pendentes()