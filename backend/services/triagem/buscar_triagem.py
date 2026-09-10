from models.triagem import Triagem

def buscar_triagem(id):
    return Triagem.buscar_por_id(id)