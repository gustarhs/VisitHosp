from datetime import datetime

def validar_atualizacao(dados):
    for campo in ["data_entrada", "data_saida"]:
        if campo in dados and dados[campo] is not None:
            try:
                dados[campo] = datetime.fromisoformat(dados[campo])
            except (TypeError, ValueError):
                raise ValueError(f"{campo} inválido.")

    return dados