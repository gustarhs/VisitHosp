from datetime import datetime

def validar_atualizacao(dados):
    if "data_nascimento" in dados and dados["data_nascimento"] is not None:
        try:
            dados["data_nascimento"] = datetime.fromisoformat(dados["data_nascimento"])
        except (TypeError, ValueError):
            raise ValueError("data_nascimento inválido.")

    return dados