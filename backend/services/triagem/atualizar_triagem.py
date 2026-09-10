from models.triagem import Triagem
from services.triagem.validar_atualizacao import validar_atualizacao

def atualizar_triagem(id, dados):
    dados = validar_atualizacao(dados)
    triagem = Triagem.buscar_por_id(id)

    if triagem is None:
        return None

    triagem.atualizar(
        data_hora=dados.get("data_hora"),
        resultado=dados.get("resultado"),
        perguntas=dados.get("perguntas"),
        respostas=dados.get("respostas")
    )

    return triagem