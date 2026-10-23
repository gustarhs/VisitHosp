from models.triagem import Triagem

def deletar_triagem(id):
    triagem = Triagem.buscar_por_id(id)

    if triagem is None:
        return False

    triagem.deletar()
    return True