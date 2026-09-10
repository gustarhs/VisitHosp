from services.internacao.validar_dados_internacao import validar_dados_internacao
from services.internacao.criar_internacao import criar_internacao
from services.internacao.listar_internacoes import listar_internacoes
from services.internacao.buscar_internacao import buscar_internacao
from services.internacao.validar_atualizacao import validar_atualizacao
from services.internacao.atualizar_internacao import atualizar_internacao
from services.internacao.deletar_internacao import deletar_internacao
from services.internacao.cancelar_por_alta import cancelar_por_alta
from services.internacao.validar_token import validar_token


class InternacaoService:
    validar_dados_internacao = staticmethod(validar_dados_internacao)
    criar_internacao = staticmethod(criar_internacao)
    listar_internacoes = staticmethod(listar_internacoes)
    buscar_internacao = staticmethod(buscar_internacao)
    validar_atualizacao = staticmethod(validar_atualizacao)
    atualizar_internacao = staticmethod(atualizar_internacao)
    deletar_internacao = staticmethod(deletar_internacao)
    cancelar_por_alta = staticmethod(cancelar_por_alta)
    validar_token = staticmethod(validar_token)
