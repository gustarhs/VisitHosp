from models.leito import Leito

class LeitoService:
    @classmethod
    def validar_dados_leito(cls, dados):
        campos_obrigatorios = ["status", "ala", "numero", "andar", "bloco"]

        for campo in campos_obrigatorios:
            valor = dados.get(campo)
            if valor is None or valor == "":
                raise ValueError(f"O campo '{campo}' é obrigatório.")

        return dados

    @classmethod
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

    @classmethod
    def listar_leitos(cls):
        return Leito.listar_todos()

    @classmethod
    def buscar_leito(cls, id):
        return Leito.buscar_por_id(id)

    @classmethod
    def atualizar_leito(cls, id, dados):
        leito = Leito.buscar_por_id(id)

        if leito is None:
            return None

        leito.atualizar(
            status=dados.get("status"),
            ala=dados.get("ala"),
            numero=dados.get("numero"),
            andar=dados.get("andar"),
            bloco=dados.get("bloco")
        )

        return leito

    @classmethod
    def deletar_leito(cls, id):
        leito = Leito.buscar_por_id(id)

        if leito is None:
            return False

        leito.deletar()
        return True
