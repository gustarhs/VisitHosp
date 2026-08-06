from datetime import datetime

from models.visita import Visita


def validar_dados_visita(dados):
    campos_obrigatorios = ["data_hora", "status", "qr_code"]

    for campo in campos_obrigatorios:
        valor = dados.get(campo)
        if valor is None or valor == "":
            raise ValueError(f"O campo '{campo}' é obrigatório.")

    try:
        dados["data_hora"] = datetime.fromisoformat(dados["data_hora"])
    except (TypeError, ValueError):
        raise ValueError("data_hora deve estar no formato YYYY-MM-DDTHH:MM:SS")

    return dados


def criar_visita(dados):
    dados = validar_dados_visita(dados)

    visita = Visita(
        data_hora=dados["data_hora"],
        status=dados["status"],
        qr_code=dados["qr_code"]
    )

    visita.salvar()
    return visita


def listar_visitas():
    return Visita.listar_todos()


def buscar_visita(id):
    return Visita.buscar_por_id(id)


def validar_atualizacao(dados):
    if "data_hora" in dados and dados["data_hora"] is not None:
        try:
            dados["data_hora"] = datetime.fromisoformat(dados["data_hora"])
        except (TypeError, ValueError):
            raise ValueError("data_hora inválido.")

    return dados


def atualizar_visita(id, dados):
    dados = validar_atualizacao(dados)
    visita = Visita.buscar_por_id(id)

    if visita is None:
        return None

    visita.atualizar(
        data_hora=dados.get("data_hora"),
        status=dados.get("status"),
        qr_code=dados.get("qr_code")
    )

    return visita


def deletar_visita(id):
    visita = Visita.buscar_por_id(id)

    if visita is None:
        return False

    visita.deletar()
    return True
