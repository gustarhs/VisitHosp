from models.paciente import Paciente
from services.paciente.validar_dados_paciente import validar_dados_paciente

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