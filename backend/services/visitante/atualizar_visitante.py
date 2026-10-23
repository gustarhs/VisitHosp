from models.visitante import Visitante
from services.visitante.validar_atualizacao import validar_atualizacao

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