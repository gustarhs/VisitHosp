from models.visitante import Visitante

def buscar_visitante(id):
    return Visitante.buscar_por_id(id)