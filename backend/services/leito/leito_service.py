from services.leito.validar_dados_leito import validar_dados_leito
from services.leito.criar_leito import criar_leito
from services.leito.listar_leitos import listar_leitos
from services.leito.buscar_leito import buscar_leito
from services.leito.atualizar_leito import atualizar_leito
from services.leito.deletar_leito import deletar_leito
from services.leito.verificar_disponibilidade_slots import verificar_disponibilidade_slots


class LeitoService:
    validar_dados_leito = staticmethod(validar_dados_leito)
    criar_leito = staticmethod(criar_leito)
    listar_leitos = staticmethod(listar_leitos)
    buscar_leito = staticmethod(buscar_leito)
    atualizar_leito = staticmethod(atualizar_leito)
    deletar_leito = staticmethod(deletar_leito)
    verificar_disponibilidade_slots = staticmethod(verificar_disponibilidade_slots)