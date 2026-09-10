from repositories.visita_repository import VisitaRepository

def validar_janela_qrcode(id_visita):
    """sp_validar_janela_qrcode: delega para a Repository."""
    return VisitaRepository.sp_validar_janela_qrcode(id_visita)