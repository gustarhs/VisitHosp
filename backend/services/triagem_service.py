from datetime import datetime

from models.triagem import Triagem


def validar_dados_triagem(dados):
    campos_obrigatorios = ["data_hora", "resultado", "perguntas", "respostas"]

    for campo in campos_obrigatorios:
        valor = dados.get(campo)
        if valor is None or valor == "":
            raise ValueError(f"O campo '{campo}' é obrigatório.")

    try:
        dados["data_hora"] = datetime.fromisoformat(dados["data_hora"])
    except (TypeError, ValueError):
        raise ValueError("data_hora deve estar no formato YYYY-MM-DDTHH:MM:SS")

    return dados


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


def listar_triagens():
    return Triagem.listar_todos()


def buscar_triagem(id):
    return Triagem.buscar_por_id(id)


def validar_atualizacao(dados):
    if "data_hora" in dados and dados["data_hora"] is not None:
        try:
            dados["data_hora"] = datetime.fromisoformat(dados["data_hora"])
        except (TypeError, ValueError):
            raise ValueError("data_hora inválido.")

    return dados


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


def deletar_triagem(id):
    triagem = Triagem.buscar_por_id(id)

    if triagem is None:
        return False

    triagem.deletar()
    return True
