from services.visitante.validar_dados_visitante import validar_dados_visitante
from services.visitante.criar_visitante import criar_visitante
from services.visitante.listar_visitantes import listar_visitantes
from services.visitante.buscar_visitante import buscar_visitante
from services.visitante.validar_atualizacao import validar_atualizacao
from services.visitante.atualizar_visitante import atualizar_visitante
from services.visitante.deletar_visitante import deletar_visitante
from services.visitante.obter_regras_acesso import obter_regras_acesso
from services.visitante.listar_pendentes import listar_pendentes


class VisitanteService:
    validar_dados_visitante = staticmethod(validar_dados_visitante)
    criar_visitante = staticmethod(criar_visitante)
    listar_visitantes = staticmethod(listar_visitantes)
    buscar_visitante = staticmethod(buscar_visitante)
    validar_atualizacao = staticmethod(validar_atualizacao)
    atualizar_visitante = staticmethod(atualizar_visitante)
    deletar_visitante = staticmethod(deletar_visitante)
    obter_regras_acesso = staticmethod(obter_regras_acesso)
    listar_pendentes = staticmethod(listar_pendentes)