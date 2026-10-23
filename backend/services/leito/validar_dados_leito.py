def validar_dados_leito(dados):
    campos_obrigatorios = ["status", "ala", "numero", "andar", "bloco"]

    for campo in campos_obrigatorios:
        valor = dados.get(campo)
        if valor is None or valor == "":
            raise ValueError(f"O campo '{campo}' é obrigatório.")

    return dados