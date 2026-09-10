from services.hospital.validar_dados_hospital import validar_dados_hospital
from services.hospital.criar_hospital import criar_hospital
from services.hospital.listar_hospitais import listar_hospitais
from services.hospital.buscar_hospital import buscar_hospital
from services.hospital.validar_atualizacao import validar_atualizacao
from services.hospital.atualizar_hospital import atualizar_hospital
from services.hospital.deletar_hospital import deletar_hospital


class HospitalService:
    validar_dados_hospital = staticmethod(validar_dados_hospital)
    criar_hospital = staticmethod(criar_hospital)
    listar_hospitais = staticmethod(listar_hospitais)
    buscar_hospital = staticmethod(buscar_hospital)
    validar_atualizacao = staticmethod(validar_atualizacao)
    atualizar_hospital = staticmethod(atualizar_hospital)
    deletar_hospital = staticmethod(deletar_hospital)