from datetime import datetime


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