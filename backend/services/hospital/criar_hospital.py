from models.hospital import Hospital
from services.hospital.validar_dados_hospital import validar_dados_hospital

def criar_hospital(dados):
    dados = validar_dados_hospital(dados)

    hospital = Hospital(
        nome=dados["nome"],
        horario_visita=dados["horario_visita"],
        rua=dados["rua"],
        numero=dados["numero"],
        cidade=dados["cidade"],
        estado=dados["estado"]
    )

    hospital.salvar()

    return hospital