from repositories.visita_repository import VisitaRepository

def validar_entrada(codigo_qrcode):
    """sp_validar_entrada_totem: delega para a Repository."""
    return VisitaRepository.sp_validar_entrada_totem(codigo_qrcode)