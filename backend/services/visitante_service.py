from datetime import datetime

from models.visitante import Visitante
from repositories.visitante_repository import VisitanteRepository

class VisitanteService:
    @classmethod
    def validar_dados_visitante(cls, dados):
        campos_obrigatorios = ["status", "tipo", "nome", "data_nascimento", "termo_consentimento", "cpf"]

        for campo in campos_obrigatorios:
            valor = dados.get(campo)
            if valor is None or valor == "":
                raise ValueError(f"O campo '{campo}' é obrigatório.")

        try:
            dados["data_nascimento"] = datetime.fromisoformat(dados["data_nascimento"])
        except (TypeError, ValueError):
            raise ValueError("data_nascimento deve estar no formato YYYY-MM-DDTHH:MM:SS")

        return dados

    @classmethod
    def criar_visitante(cls, dados):
        dados = cls.validar_dados_visitante(dados)

        visitante = Visitante(
            status=dados["status"],
            tipo=dados["tipo"],
            nome=dados["nome"],
            data_nascimento=dados["data_nascimento"],
            termo_consentimento=dados["termo_consentimento"],
            cpf=dados["cpf"]
        )

        visitante.salvar()
        return visitante

    @classmethod
    def listar_visitantes(cls):
        return Visitante.listar_todos()

    @classmethod
    def buscar_visitante(cls, id):
        return Visitante.buscar_por_id(id)

    @classmethod
    def validar_atualizacao(cls, dados):
        if "data_nascimento" in dados and dados["data_nascimento"] is not None:
            try:
                dados["data_nascimento"] = datetime.fromisoformat(dados["data_nascimento"])
            except (TypeError, ValueError):
                raise ValueError("data_nascimento inválido.")

        return dados

    @classmethod
    def atualizar_visitante(cls, id, dados):
        dados = cls.validar_atualizacao(dados)
        visitante = Visitante.buscar_por_id(id)

        if visitante is None:
            return None

        visitante.atualizar(
            status=dados.get("status"),
            tipo=dados.get("tipo"),
            nome=dados.get("nome"),
            data_nascimento=dados.get("data_nascimento"),
            termo_consentimento=dados.get("termo_consentimento"),
            cpf=dados.get("cpf")
        )

        return visitante

    @classmethod
    def deletar_visitante(cls, id):
        visitante = Visitante.buscar_por_id(id)

        if visitante is None:
            return False

        visitante.deletar()
        return True

    @classmethod
    def obter_regras_acesso(cls, id_visitante):
        """sp_obter_regras_acesso_por_papel: delega para a Repository."""
        return VisitanteRepository.sp_obter_regras_acesso_por_papel(id_visitante)

    @classmethod
    def listar_pendentes(cls):
        """sp_listar_cadastros_pendentes: delega para a Repository."""
        return VisitanteRepository.sp_listar_cadastros_pendentes()
