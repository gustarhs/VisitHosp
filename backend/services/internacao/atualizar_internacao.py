from models.internacao import Internacao
from services.internacao.validar_atualizacao import validar_atualizacao

def atualizar_internacao(id, dados):
    dados = validar_atualizacao(dados)
    internacao = Internacao.buscar_por_id(id)

    if internacao is None:
        return None

    internacao.atualizar(
        data_entrada=dados.get("data_entrada"),
        data_saida=dados.get("data_saida"),
        status=dados.get("status"),
        token_acesso=dados.get("token_acesso")
    )

    return internacao