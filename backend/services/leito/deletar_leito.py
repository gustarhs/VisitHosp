from models.leito import Leito

def deletar_leito(id):
    leito = Leito.buscar_por_id(id)

    if leito is None:
        return False

    leito.deletar()
    return True