from models.paciente import Paciente
from services.paciente.validar_atualizacao import validar_atualizacao

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