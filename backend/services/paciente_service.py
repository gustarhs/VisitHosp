from datetime import datetime

from models.paciente import Paciente
from repositories.paciente_repository import PacienteRepository

class PacienteService:
    @classmethod
    def validar_dados_paciente(cls, dados):
        campos_obrigatorios = ["data_nascimento", "tipo", "status", "nome", "cpf"]

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
    def criar_paciente(cls, dados):
        dados = cls.validar_dados_paciente(dados)

        paciente = Paciente(
            data_nascimento=dados["data_nascimento"],
            tipo=dados["tipo"],
            status=dados["status"],
            nome=dados["nome"],
            cpf=dados["cpf"]
        )

        paciente.salvar()
        return paciente

    @classmethod
    def listar_pacientes(cls):
        return Paciente.listar_todos()

    @classmethod
    def buscar_paciente(cls, id):
        return Paciente.buscar_por_id(id)

    @classmethod
    def validar_atualizacao(cls, dados):
        if "data_nascimento" in dados and dados["data_nascimento"] is not None:
            try:
                dados["data_nascimento"] = datetime.fromisoformat(dados["data_nascimento"])
            except (TypeError, ValueError):
                raise ValueError("data_nascimento inválido.")

        return dados

    @classmethod
    def atualizar_paciente(cls, id, dados):
        dados = cls.validar_atualizacao(dados)
        paciente = Paciente.buscar_por_id(id)

        if paciente is None:
            return None

        paciente.atualizar(
            data_nascimento=dados.get("data_nascimento"),
            tipo=dados.get("tipo"),
            status=dados.get("status"),
            nome=dados.get("nome"),
            cpf=dados.get("cpf")
        )

        return paciente

    @classmethod
    def deletar_paciente(cls, id):
        paciente = Paciente.buscar_por_id(id)

        if paciente is None:
            return False

        paciente.deletar()
        return True

    @classmethod
    def verificar_bloqueio(cls, id_paciente):
        """sp_verificar_bloqueio_status_paciente: delega para a Repository."""
        return PacienteRepository.sp_verificar_bloqueio_status_paciente(id_paciente)

    @classmethod
    def obter_responsavel(cls, id_paciente):
        """sp_obter_responsavel_autorizado: delega para a Repository (fallback ADM1 -> ADM2)."""
        return PacienteRepository.sp_obter_responsavel_autorizado(id_paciente)
