from models.internacao import Internacao

def deletar_internacao(id):
    internacao = Internacao.buscar_por_id(id)

    if internacao is None:
        return False

    internacao.deletar()
    return True