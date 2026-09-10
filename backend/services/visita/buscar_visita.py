from models.visita import Visita

def buscar_visita(id):
    return Visita.buscar_por_id(id)