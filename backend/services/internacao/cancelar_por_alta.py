from repositories.internacao_repository import InternacaoRepository

def cancelar_por_alta(id_leito):
    """sp_cancelar_acessos_por_alta: dispara a invalidação em lote via Repository."""
    return InternacaoRepository.sp_cancelar_acessos_por_alta(id_leito)