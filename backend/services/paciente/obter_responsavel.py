from repositories.paciente_repository import PacienteRepository

def obter_responsavel(id_paciente):
    """sp_obter_responsavel_autorizado: delega para a Repository (fallback ADM1 -> ADM2)."""
    return PacienteRepository.sp_obter_responsavel_autorizado(id_paciente)