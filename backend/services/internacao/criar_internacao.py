from models.internacao import Internacao
from services.internacao.validar_dados_internacao import validar_dados_internacao

def criar_internacao(dados):
    dados = validar_dados_internacao(dados)

    internacao = Internacao(
        data_entrada=dados["data_entrada"],
        data_saida=dados["data_saida"],
        status=dados["status"],
        token_acesso=dados["token_acesso"]
    )

    internacao.salvar()
    return internacao