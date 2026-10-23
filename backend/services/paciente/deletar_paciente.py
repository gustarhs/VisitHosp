from models.paciente import Paciente

def deletar_paciente(id):
    paciente = Paciente.buscar_por_id(id)

    if paciente is None:
        return False

    paciente.deletar()
    return True