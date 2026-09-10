from datetime import datetime

def validar_dados_visitante(dados):
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