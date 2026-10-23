from datetime import datetime

def validar_dados_visita(dados):
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