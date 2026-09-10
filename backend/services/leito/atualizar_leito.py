from models.leito import Leito

def atualizar_leito(id, dados):
    leito = Leito.buscar_por_id(id)

    if leito is None:
        return None

    leito.atualizar(
        status=dados.get("status"),
        ala=dados.get("ala"),
        numero=dados.get("numero"),
        andar=dados.get("andar"),
        bloco=dados.get("bloco")
    )

    return leito