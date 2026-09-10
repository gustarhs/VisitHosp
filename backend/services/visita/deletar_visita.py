from models.visita import Visita

def deletar_visita(id):
    visita = Visita.buscar_por_id(id)

    if visita is None:
        return False

    visita.deletar()
    return True