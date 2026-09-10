from datetime import datetime

def validar_dados_internacao(dados):
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