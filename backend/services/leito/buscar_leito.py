from models.leito import Leito

def buscar_leito(id):
    return Leito.buscar_por_id(id)