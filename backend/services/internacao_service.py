from datetime import datetime

from models.internacao import Internacao

class InternacaoService:
    @classmethod
    def validar_dados_internacao(cls, dados):
        campos_obrigatorios = [
            "data_entrada",
            "data_saida",
            "status",
            "token_acesso"
        ]

        for campo in campos_obrigatorios:
            valor = dados.get(campo)
            if valor is None or valor == "":
                raise ValueError(f"O campo '{campo}' é obrigatório.")

        for campo in ["data_entrada", "data_saida"]:
            try:
                dados[campo] = datetime.fromisoformat(dados[campo])
            except (TypeError, ValueError):
                raise ValueError(f"{campo} deve estar no formato YYYY-MM-DDTHH:MM:SS")

        return dados

    @classmethod
    def criar_internacao(cls, dados):
        dados = cls.validar_dados_internacao(dados)

        internacao = Internacao(
            data_entrada=dados["data_entrada"],
            data_saida=dados["data_saida"],
            status=dados["status"],
            token_acesso=dados["token_acesso"]
        )

        internacao.salvar()
        return internacao

    @classmethod
    def listar_internacoes(cls):
        return Internacao.listar_todos()

    @classmethod
    def buscar_internacao(cls, id):
        return Internacao.buscar_por_id(id)

    @classmethod
    def validar_atualizacao(cls, dados):
        for campo in ["data_entrada", "data_saida"]:
            if campo in dados and dados[campo] is not None:
                try:
                    dados[campo] = datetime.fromisoformat(dados[campo])
                except (TypeError, ValueError):
                    raise ValueError(f"{campo} inválido.")

        return dados

    @classmethod
    def atualizar_internacao(cls, id, dados):
        dados = cls.validar_atualizacao(dados)
        internacao = Internacao.buscar_por_id(id)

        if internacao is None:
            return None

        internacao.atualizar(
            data_entrada=dados.get("data_entrada"),
            data_saida=dados.get("data_saida"),
            status=dados.get("status"),
            token_acesso=dados.get("token_acesso")
        )

        return internacao

    @classmethod
    def deletar_internacao(cls, id):
        internacao = Internacao.buscar_por_id(id)

        if internacao is None:
            return False

        internacao.deletar()
        return True