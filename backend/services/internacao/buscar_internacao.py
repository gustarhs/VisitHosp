from models.internacao import Internacao

def buscar_internacao(id):
    return Internacao.buscar_por_id(id)