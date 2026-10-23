from models.visitante import Visitante
from services.visitante.validar_dados_visitante import validar_dados_visitante

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