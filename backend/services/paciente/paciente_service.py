from services.paciente.validar_dados_paciente import validar_dados_paciente
from services.paciente.criar_paciente import criar_paciente
from services.paciente.listar_pacientes import listar_pacientes
from services.paciente.buscar_paciente import buscar_paciente
from services.paciente.validar_atualizacao import validar_atualizacao
from services.paciente.atualizar_paciente import atualizar_paciente
from services.paciente.deletar_paciente import deletar_paciente
from services.paciente.verificar_bloqueio import verificar_bloqueio
from services.paciente.obter_responsavel import obter_responsavel


class PacienteService:
    validar_dados_paciente = staticmethod(validar_dados_paciente)
    criar_paciente = staticmethod(criar_paciente)
    listar_pacientes = staticmethod(listar_pacientes)
    buscar_paciente = staticmethod(buscar_paciente)
    validar_atualizacao = staticmethod(validar_atualizacao)
    atualizar_paciente = staticmethod(atualizar_paciente)
    deletar_paciente = staticmethod(deletar_paciente)
    verificar_bloqueio = staticmethod(verificar_bloqueio)
    obter_responsavel = staticmethod(obter_responsavel)