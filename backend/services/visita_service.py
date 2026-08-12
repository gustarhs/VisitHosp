from datetime import datetime

from models.visita import Visita

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
