from models.triagem import Triagem
from services.triagem.validar_dados_triagem import validar_dados_triagem


def criar_triagem(dados):
    dados = validar_dados_triagem(dados)

    triagem = Triagem(
        data_hora=dados["data_hora"],
        resultado=dados["resultado"],
        perguntas=dados["perguntas"],
        respostas=dados["respostas"]
    )

    triagem.salvar()
    return triagem