from models.paciente import Paciente

def buscar_paciente(id):
    return Paciente.buscar_por_id(id)