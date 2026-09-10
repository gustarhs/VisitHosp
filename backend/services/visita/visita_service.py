from services.visita.validar_dados_visita import validar_dados_visita
from services.visita.criar_visita import criar_visita
from services.visita.listar_visitas import listar_visitas
from services.visita.buscar_visita import buscar_visita
from services.visita.validar_atualizacao import validar_atualizacao
from services.visita.atualizar_visita import atualizar_visita
from services.visita.deletar_visita import deletar_visita
from services.visita.historico_por_paciente import historico_por_paciente
from services.visita.relatorio_auditoria import relatorio_auditoria
from services.visita.relatorio_gerencial import relatorio_gerencial
from services.visita.verificar_extensao import verificar_extensao
from services.visita.validar_janela_qrcode import validar_janela_qrcode
from services.visita.validar_entrada import validar_entrada
from services.visita.horarios_disponiveis import horarios_disponiveis
from services.visita._helpers import SLOTS_PADRAO, CAPACIDADE_MAXIMA_POR_HORARIO


class VisitaService:
    SLOTS_PADRAO = SLOTS_PADRAO
    CAPACIDADE_MAXIMA_POR_HORARIO = CAPACIDADE_MAXIMA_POR_HORARIO

    validar_dados_visita = staticmethod(validar_dados_visita)
    criar_visita = staticmethod(criar_visita)
    listar_visitas = staticmethod(listar_visitas)
    buscar_visita = staticmethod(buscar_visita)
    validar_atualizacao = staticmethod(validar_atualizacao)
    atualizar_visita = staticmethod(atualizar_visita)
    deletar_visita = staticmethod(deletar_visita)
    historico_por_paciente = staticmethod(historico_por_paciente)
    relatorio_auditoria = staticmethod(relatorio_auditoria)
    relatorio_gerencial = staticmethod(relatorio_gerencial)
    verificar_extensao = staticmethod(verificar_extensao)
    validar_janela_qrcode = staticmethod(validar_janela_qrcode)
    validar_entrada = staticmethod(validar_entrada)
    horarios_disponiveis = staticmethod(horarios_disponiveis)