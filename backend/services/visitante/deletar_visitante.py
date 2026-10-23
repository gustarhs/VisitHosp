from models.visitante import Visitante

def deletar_visitante(id):
    visitante = Visitante.buscar_por_id(id)

    if visitante is None:
        return False

    visitante.deletar()
    return True