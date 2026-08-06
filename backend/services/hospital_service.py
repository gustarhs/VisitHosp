from datetime import datetime
from models.hospital import Hospital

def validar_dados_hospital(dados):

    campos_obrigatorios = [
        "nome",
        "horario_visita",
        "rua",
        "numero",
        "cidade",
        "estado"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo):
            raise ValueError(f"O campo '{campo}' é obrigatório.")

    try:
        dados["horario_visita"] = datetime.fromisoformat(
            dados["horario_visita"]
        )
    except ValueError:
        raise ValueError(
            "horario_visita deve estar no formato YYYY-MM-DDTHH:MM:SS"
        )

    return dados

def criar_hospital(dados):

    dados = validar_dados_hospital(dados)

    hospital = Hospital(
        nome=dados["nome"],
        horario_visita=dados["horario_visita"],
        rua=dados["rua"],
        numero=dados["numero"],
        cidade=dados["cidade"],
        estado=dados["estado"]
    )

    hospital.salvar()

    return hospital


def listar_hospitais():
    return Hospital.listar_todos()


def buscar_hospital(id):
    return Hospital.buscar_por_id(id)

def validar_atualizacao(dados):
    if "horario_visita" in dados:
        try:
            dados["horario_visita"] = datetime.fromisoformat(
                dados["horario_visita"]
            )
        except ValueError:
            raise ValueError(
                "horario_visita inválido."
            )

    return dados

def atualizar_hospital(id, dados):

    dados = validar_atualizacao(dados)
    hospital = Hospital.buscar_por_id(id)

    if hospital is None:
        return None

    hospital.atualizar(
        nome=dados.get("nome"),
        horario_visita=dados.get("horario_visita"),
        rua=dados.get("rua"),
        numero=dados.get("numero"),
        cidade=dados.get("cidade"),
        estado=dados.get("estado")
    )

    return hospital


def deletar_hospital(id):

    hospital = Hospital.buscar_por_id(id)

    if hospital is None:
        return False

    hospital.deletar()

    return True