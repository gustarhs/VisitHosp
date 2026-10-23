from datetime import datetime

def validar_atualizacao(dados):
    if "data_hora" in dados and dados["data_hora"] is not None:
        try:
            dados["data_hora"] = datetime.fromisoformat(dados["data_hora"])
        except (TypeError, ValueError):
            raise ValueError("data_hora inválido.")

    return dados