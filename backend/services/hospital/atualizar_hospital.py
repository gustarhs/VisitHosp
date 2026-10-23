from models.hospital import Hospital
from services.hospital.validar_atualizacao import validar_atualizacao

def atualizar_hospital(id, dados):
    dados = validar_atualizacao(dados)
    hospital = Hospital.buscar_por_id(id)

    if hospital is None:
        return None

    hospital.atualizar(
        nome=dados.get("nome"),
        horario_visita=dados.get("horario_visita"),
        rua=dados.get("rua"),
        numero=dados.get("numero"),
        cidade=dados.get("cidade"),
        estado=dados.get("estado")
    )

    return hospital