from datetime import datetime

from models.paciente import Paciente


def validar_dados_paciente(dados):
    campos_obrigatorios = ["data_nascimento", "tipo", "status", "nome", "cpf"]

    for campo in campos_obrigatorios:
        valor = dados.get(campo)
        if valor is None or valor == "":
            raise ValueError(f"O campo '{campo}' é obrigatório.")

    try:
        dados["data_nascimento"] = datetime.fromisoformat(dados["data_nascimento"])
    except (TypeError, ValueError):
        raise ValueError("data_nascimento deve estar no formato YYYY-MM-DDTHH:MM:SS")

    return dados


def criar_paciente(dados):
    dados = validar_dados_paciente(dados)

    paciente = Paciente(
        data_nascimento=dados["data_nascimento"],
        tipo=dados["tipo"],
        status=dados["status"],
        nome=dados["nome"],
        cpf=dados["cpf"]
    )

    paciente.salvar()
    return paciente


def listar_pacientes():
    return Paciente.listar_todos()


def buscar_paciente(id):
    return Paciente.buscar_por_id(id)


def validar_atualizacao(dados):
    if "data_nascimento" in dados and dados["data_nascimento"] is not None:
        try:
            dados["data_nascimento"] = datetime.fromisoformat(dados["data_nascimento"])
        except (TypeError, ValueError):
            raise ValueError("data_nascimento inválido.")

    return dados


def atualizar_paciente(id, dados):
    dados = validar_atualizacao(dados)
    paciente = Paciente.buscar_por_id(id)

    if paciente is None:
        return None

    paciente.atualizar(
        data_nascimento=dados.get("data_nascimento"),
        tipo=dados.get("tipo"),
        status=dados.get("status"),
        nome=dados.get("nome"),
        cpf=dados.get("cpf")
    )

    return paciente


def deletar_paciente(id):
    paciente = Paciente.buscar_por_id(id)

    if paciente is None:
        return False

    paciente.deletar()
    return True
