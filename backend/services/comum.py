"""
Utilitarios compartilhados pelos servicos dos novos requisitos
(consulta, agendamento, vinculo e acesso/auditoria).
"""
from datetime import datetime, time, timedelta

from extensions import db
from models import Visita, RegistroAcesso
from services.visita._helpers import SLOTS_PADRAO, CAPACIDADE_MAXIMA_POR_HORARIO

# Regras de negocio (ajuste aqui se o hospital mudar a politica)
DURACAO_SLOT_MINUTOS = 30
JANELA_CHECKIN_ANTES_MINUTOS = 20       # check-in liberado a partir de X min antes
JANELA_CHECKIN_DEPOIS_MINUTOS = 30      # ...ate X min depois do horario agendado
PERMANENCIA_MAXIMA_MINUTOS = 60
ANTECEDENCIA_MINIMA_ALTERACAO_MINUTOS = 60  # alterar/cancelar com no minimo X min de antecedencia

SITUACOES = {
    "agendada": "Agendada",
    "em_andamento": "Em andamento",
    "concluida": "Concluída",
    "cancelada": "Cancelada",
    "nao_compareceu": "Não compareceu",
}


class ErroServico(Exception):
    status = 400


class Invalido(ErroServico):
    status = 400


class Proibido(ErroServico):
    status = 403


class NaoEncontrado(ErroServico):
    status = 404


class Conflito(ErroServico):
    status = 409


def parse_data(valor, nome_campo, fim_do_dia=False):
    """Aceita 'YYYY-MM-DD' ou ISO 8601 completo."""
    if valor is None or str(valor).strip() == "":
        raise Invalido(f"O parâmetro '{nome_campo}' é obrigatório.")
    texto = str(valor).strip().replace("Z", "")
    try:
        dt = datetime.fromisoformat(texto)
    except ValueError:
        raise Invalido(f"'{nome_campo}' inválido. Use YYYY-MM-DD ou ISO 8601 (ex: 2026-10-22T14:00:00).")
    if len(texto) == 10 and fim_do_dia:
        dt = datetime.combine(dt.date(), time(23, 59, 59))
    return dt.replace(tzinfo=None)


def parse_periodo(inicio_str, fim_str, dias_padrao=30):
    """Periodo opcional: padrao = ultimos `dias_padrao` dias ate o fim de hoje."""
    agora = datetime.now()
    fim = parse_data(fim_str, "periodo_fim", fim_do_dia=True) if fim_str else datetime.combine(agora.date(), time(23, 59, 59))
    inicio = parse_data(inicio_str, "periodo_inicio") if inicio_str else datetime.combine((fim - timedelta(days=dias_padrao)).date(), time.min)
    if inicio > fim:
        raise Invalido("O período inicial não pode ser maior que o período final.")
    return inicio, fim


def inicio_do_slot(data_hora):
    """Retorna (inicio, fim) do horario oficial que contem data_hora, ou None."""
    for ini_str, fim_str in SLOTS_PADRAO:
        ini = datetime.combine(data_hora.date(), datetime.strptime(ini_str, "%H:%M").time())
        fim = datetime.combine(data_hora.date(), datetime.strptime(fim_str, "%H:%M").time())
        if ini <= data_hora < fim:
            return ini, fim
    return None


def contar_ocupacao(id_leito, inicio, fim, ignorar_visita=None):
    """Visitas ativas no leito (via internacao) com horario em [inicio, fim)."""
    from models import Internacao
    consulta = (
        db.session.query(db.func.count(Visita.id))
        .join(Internacao, Visita.id_internacao == Internacao.id)
        .filter(
            Internacao.id_leito == id_leito,
            Visita.status == True,  # noqa: E712
            Visita.data_hora >= inicio,
            Visita.data_hora < fim,
        )
    )
    if ignorar_visita is not None:
        consulta = consulta.filter(Visita.id != ignorar_visita)
    return consulta.scalar() or 0


def registros_por_visita(ids_visita):
    """{id_visita: {'checkin': RegistroAcesso|None, 'checkout': RegistroAcesso|None}}"""
    mapa = {i: {"checkin": None, "checkout": None} for i in ids_visita}
    if not ids_visita:
        return mapa
    registros = (
        RegistroAcesso.query
        .filter(RegistroAcesso.id_visita.in_(list(ids_visita)))
        .order_by(RegistroAcesso.data_hora.asc(), RegistroAcesso.id.asc())
        .all()
    )
    for r in registros:
        if r.tipo == RegistroAcesso.TIPO_CHECKIN and mapa[r.id_visita]["checkin"] is None:
            mapa[r.id_visita]["checkin"] = r
        elif r.tipo == RegistroAcesso.TIPO_CHECKOUT:
            mapa[r.id_visita]["checkout"] = r
    return mapa


def situacao_visita(visita, checkin, checkout, agora=None):
    agora = agora or datetime.now()
    if not visita.status:
        return "cancelada"
    if checkout is not None:
        return "concluida"
    if checkin is not None:
        return "em_andamento"
    if visita.data_hora + timedelta(minutes=JANELA_CHECKIN_DEPOIS_MINUTOS) < agora:
        return "nao_compareceu"
    return "agendada"


def minutos_entre(inicio, fim):
    if inicio is None or fim is None:
        return None
    return int(round((fim - inicio).total_seconds() / 60))


def pode_alterar(visita, checkin, agora=None):
    agora = agora or datetime.now()
    if not visita.status or checkin is not None:
        return False
    return visita.data_hora - agora >= timedelta(minutes=ANTECEDENCIA_MINIMA_ALTERACAO_MINUTOS)


def dict_leito(leito):
    if leito is None:
        return None
    return {"id": leito.id, "numero": leito.numero, "ala": leito.ala, "andar": leito.andar, "bloco": leito.bloco}
