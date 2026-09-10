from datetime import datetime

from models.visita import Visita
from services.visita._helpers import SLOTS_PADRAO, CAPACIDADE_MAXIMA_POR_HORARIO

def horarios_disponiveis(id_internacao, data_str):
    """
    Retorna, para uma internação e uma data (YYYY-MM-DD), a lista de
    horários fixos de visita com a ocupação atual de cada um
    (quantas visitas ativas já estão marcadas ali).
    """
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValueError("Parâmetro 'data' inválido. Use o formato YYYY-MM-DD")

    resultado = []

    for inicio_str, fim_str in SLOTS_PADRAO:
        inicio = datetime.combine(data, datetime.strptime(inicio_str, "%H:%M").time())
        fim = datetime.combine(data, datetime.strptime(fim_str, "%H:%M").time())

        ocupacao = Visita.query.filter(
            Visita.id_internacao == id_internacao,
            Visita.status == True,  # noqa: E712
            Visita.data_hora >= inicio,
            Visita.data_hora < fim,
        ).count()

        resultado.append({
            "horario": f"{inicio_str} - {fim_str}",
            "inicio": inicio.isoformat(),
            "ocupacao": ocupacao,
            "capacidade": CAPACIDADE_MAXIMA_POR_HORARIO,
        })

    return resultado