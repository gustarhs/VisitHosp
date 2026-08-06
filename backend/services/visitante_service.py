from datetime import datetime

from models.visitante import Visitante


def validar_dados_visitante(dados):
    campos_obrigatorios = ["status", "tipo", "nome", "data_nascimento", "termo_consentimento", "cpf"]

    for campo in campos_obrigatorios:
        valor = dados.get(campo)
        if valor is None or valor == "":
            raise ValueError(f"O campo '{campo}' é obrigatório.")

    try:
        dados["data_nascimento"] = datetime.fromisoformat(dados["data_nascimento"])
    except (TypeError, ValueError):
        raise ValueError("data_nascimento deve estar no formato YYYY-MM-DDTHH:MM:SS")

    return dados


def criar_visitante(dados):
    dados = validar_dados_visitante(dados)

    visitante = Visitante(
        status=dados["status"],
        tipo=dados["tipo"],
        nome=dados["nome"],
        data_nascimento=dados["data_nascimento"],
        termo_consentimento=dados["termo_consentimento"],
        cpf=dados["cpf"]
    )

    visitante.salvar()
    return visitante


def listar_visitantes():
    return Visitante.listar_todos()


def buscar_visitante(id):
    return Visitante.buscar_por_id(id)


def validar_atualizacao(dados):
    if "data_nascimento" in dados and dados["data_nascimento"] is not None:
        try:
            dados["data_nascimento"] = datetime.fromisoformat(dados["data_nascimento"])
        except (TypeError, ValueError):
            raise ValueError("data_nascimento inválido.")

    return dados


def atualizar_visitante(id, dados):
    dados = validar_atualizacao(dados)
    visitante = Visitante.buscar_por_id(id)

    if visitante is None:
        return None

    visitante.atualizar(
        status=dados.get("status"),
        tipo=dados.get("tipo"),
        nome=dados.get("nome"),
        data_nascimento=dados.get("data_nascimento"),
        termo_consentimento=dados.get("termo_consentimento"),
        cpf=dados.get("cpf")
    )

    return visitante


def deletar_visitante(id):
    visitante = Visitante.buscar_por_id(id)

    if visitante is None:
        return False

    visitante.deletar()
    return True
