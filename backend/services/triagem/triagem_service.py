from services.triagem.validar_dados_triagem import validar_dados_triagem
from services.triagem.criar_triagem import criar_triagem
from services.triagem.listar_triagens import listar_triagens
from services.triagem.buscar_triagem import buscar_triagem
from services.triagem.validar_atualizacao import validar_atualizacao
from services.triagem.atualizar_triagem import atualizar_triagem
from services.triagem.deletar_triagem import deletar_triagem


class TriagemService:
    validar_dados_triagem = staticmethod(validar_dados_triagem)
    criar_triagem = staticmethod(criar_triagem)
    listar_triagens = staticmethod(listar_triagens)
    buscar_triagem = staticmethod(buscar_triagem)
    validar_atualizacao = staticmethod(validar_atualizacao)
    atualizar_triagem = staticmethod(atualizar_triagem)
    deletar_triagem = staticmethod(deletar_triagem)