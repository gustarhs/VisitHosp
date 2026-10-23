from models.visita import Visita
from services.visita.validar_dados_visita import validar_dados_visita

def criar_visita(dados):
    dados = validar_dados_visita(dados)

    visita = Visita(
        data_hora=dados["data_hora"],
        status=dados["status"],
        qr_code=dados["qr_code"]
    )

    visita.salvar()
    return visita