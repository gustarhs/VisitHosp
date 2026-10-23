from repositories.internacao_repository import InternacaoRepository

def validar_token(codigo_token):
    """sp_validar_token_acesso: delega para a Repository."""
    return InternacaoRepository.sp_validar_token_acesso(codigo_token)