from repositories.paciente_repository import PacienteRepository

def verificar_bloqueio(id_paciente):
    """sp_verificar_bloqueio_status_paciente: delega para a Repository."""
    return PacienteRepository.sp_verificar_bloqueio_status_paciente(id_paciente)