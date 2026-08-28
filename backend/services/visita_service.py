from datetime import datetime

from models.visita import Visita
from repositories.visita_repository import VisitaRepository

class VisitaService:
    @classmethod
    def validar_dados_visita(cls, dados):
        campos_obrigatorios = ["data_hora", "status", "qr_code"]

        for campo in campos_obrigatorios:
            valor = dados.get(campo)
            if valor is None or valor == "":
                raise ValueError(f"O campo '{campo}' é obrigatório.")

        try:
            dados["data_hora"] = datetime.fromisoformat(dados["data_hora"])
        except (TypeError, ValueError):
            raise ValueError("data_hora deve estar no formato YYYY-MM-DDTHH:MM:SS")

        return dados

    @classmethod
    def criar_visita(cls, dados):
        dados = cls.validar_dados_visita(dados)

        visita = Visita(
            data_hora=dados["data_hora"],
            status=dados["status"],
            qr_code=dados["qr_code"]
        )

        visita.salvar()
        return visita

    @classmethod
    def listar_visitas(cls):
        return Visita.listar_todos()

    @classmethod
    def buscar_visita(cls, id):
        return Visita.buscar_por_id(id)

    @classmethod
    def validar_atualizacao(cls, dados):
        if "data_hora" in dados and dados["data_hora"] is not None:
            try:
                dados["data_hora"] = datetime.fromisoformat(dados["data_hora"])
            except (TypeError, ValueError):
                raise ValueError("data_hora inválido.")

        return dados

    @classmethod
    def atualizar_visita(cls, id, dados):
        dados = cls.validar_atualizacao(dados)
        visita = Visita.buscar_por_id(id)

        if visita is None:
            return None

        visita.atualizar(
            data_hora=dados.get("data_hora"),
            status=dados.get("status"),
            qr_code=dados.get("qr_code")
        )

        return visita

    @classmethod
    def deletar_visita(cls, id):
        visita = Visita.buscar_por_id(id)

        if visita is None:
            return False

        visita.deletar()
        return True

    @classmethod
    def historico_por_paciente(cls, id_paciente, data_inicio_str=None, data_fim_str=None):
        """sp_historico_visitas_paciente: valida datas opcionais e delega para a Repository."""
        data_inicio = cls._parse_data_opcional(data_inicio_str, "data_inicio")
        data_fim = cls._parse_data_opcional(data_fim_str, "data_fim")
        return VisitaRepository.sp_historico_visitas_paciente(id_paciente, data_inicio, data_fim)

    @classmethod
    def relatorio_auditoria(cls, periodo_inicio_str, periodo_fim_str, id_leito=None):
        """sp_relatorio_auditoria_fluxo: valida o período obrigatório e delega para a Repository."""
        periodo_inicio = cls._parse_data_obrigatoria(periodo_inicio_str, "periodo_inicio")
        periodo_fim = cls._parse_data_obrigatoria(periodo_fim_str, "periodo_fim")
        return VisitaRepository.sp_relatorio_auditoria_fluxo(id_leito, periodo_inicio, periodo_fim)

    @classmethod
    def relatorio_gerencial(cls, periodo_inicio_str, periodo_fim_str, id_paciente=None):
        """sp_relatorio_gerencial_visitas: valida o período obrigatório e delega para a Repository."""
        periodo_inicio = cls._parse_data_obrigatoria(periodo_inicio_str, "periodo_inicio")
        periodo_fim = cls._parse_data_obrigatoria(periodo_fim_str, "periodo_fim")
        return VisitaRepository.sp_relatorio_gerencial_visitas(periodo_inicio, periodo_fim, id_paciente)

    @classmethod
    def verificar_extensao(cls, id_leito, horario_agendado_str):
        """sp_verificar_slot_extensao: valida o horário e delega para a Repository."""
        horario_agendado = cls._parse_data_obrigatoria(horario_agendado_str, "horario_agendado")
        return VisitaRepository.sp_verificar_slot_extensao(id_leito, horario_agendado)

    @classmethod
    def validar_janela_qrcode(cls, id_visita):
        """sp_validar_janela_qrcode: delega para a Repository."""
        return VisitaRepository.sp_validar_janela_qrcode(id_visita)

    @classmethod
    def validar_entrada(cls, codigo_qrcode):
        """sp_validar_entrada_totem: delega para a Repository."""
        return VisitaRepository.sp_validar_entrada_totem(codigo_qrcode)

    @classmethod
    def _parse_data_opcional(cls, valor, nome_campo):
        if not valor:
            return None
        return cls._parse_data_obrigatoria(valor, nome_campo)

    @classmethod
    def _parse_data_obrigatoria(cls, valor, nome_campo):
        try:
            return datetime.fromisoformat(valor)
        except (TypeError, ValueError):
            raise ValueError(f"{nome_campo} deve estar no formato ISO 8601 (ex: 2026-09-01T14:00:00)")
