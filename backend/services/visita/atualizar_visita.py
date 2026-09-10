from models.visita import Visita
from services.visita.validar_atualizacao import validar_atualizacao

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