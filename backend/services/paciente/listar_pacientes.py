from models.paciente import Paciente

def listar_pacientes():
    return Paciente.listar_todos()