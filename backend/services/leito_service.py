from models.leito import Leito


def validar_dados_leito(dados):
    campos_obrigatorios = ["status", "ala", "numero", "andar", "bloco"]

    for campo in campos_obrigatorios:
        valor = dados.get(campo)
        if valor is None or valor == "":
            raise ValueError(f"O campo '{campo}' é obrigatório.")

    return dados


def criar_leito(dados):
    dados = validar_dados_leito(dados)

    leito = Leito(
        status=dados["status"],
        ala=dados["ala"],
        numero=dados["numero"],
        andar=dados["andar"],
        bloco=dados["bloco"]
    )

    leito.salvar()
    return leito


def listar_leitos():
    return Leito.listar_todos()


def buscar_leito(id):
    return Leito.buscar_por_id(id)

def atualizar_leito(id, dados):

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


def deletar_leito(id):
    leito = Leito.buscar_por_id(id)

    if leito is None:
        return False

    leito.deletar()
    return True
