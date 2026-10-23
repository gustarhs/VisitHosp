from models.leito import Leito
from repositories.leito_repository import LeitoRepository

def criar_leito(cls, dados):
        dados = cls.validar_dados_leito(dados)

        leito = Leito(
            status=dados["status"],
            ala=dados["ala"],
            numero=dados["numero"],
            andar=dados["andar"],
            bloco=dados["bloco"]
        )

        leito.salvar()
        return leito