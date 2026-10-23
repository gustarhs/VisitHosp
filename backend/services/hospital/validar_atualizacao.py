from datetime import datetime

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