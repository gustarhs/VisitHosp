from datetime import datetime, timedelta

from extensions import db
from models import Visita, Visitante, Internacao, Paciente, Leito, RegistroAcesso
from services.comum import (
    NaoEncontrado, Conflito, Proibido, parse_periodo, registros_por_visita, situacao_visita,
    minutos_entre, dict_leito, SITUACOES,
    JANELA_CHECKIN_ANTES_MINUTOS, JANELA_CHECKIN_DEPOIS_MINUTOS, PERMANENCIA_MAXIMA_MINUTOS,
)

ALERTAS = {
    "checkin_fora_da_janela": "Check-in fora da janela permitida",
    "permanencia_excedida": "Permanência acima do limite",
    "sem_checkout": "Sem check-out registrado",
}

# (nome, hora inicial, hora final exclusiva)
TURNOS = [
    ("Manhã", 6, 12),
    ("Tarde", 12, 18),
    ("Noite", 18, 24),
    ("Madrugada", 0, 6),
]


def _iso(dt):
    return dt.isoformat() if dt else None


def _linha(visita, visitante, paciente, leito, checkin, checkout, agora):
    ci = checkin.data_hora if checkin else None
    co = checkout.data_hora if checkout else None
    situacao = situacao_visita(visita, checkin, checkout, agora)

    alertas = []
    if ci is not None:
        inicio_ok = visita.data_hora - timedelta(minutes=JANELA_CHECKIN_ANTES_MINUTOS)
        fim_ok = visita.data_hora + timedelta(minutes=JANELA_CHECKIN_DEPOIS_MINUTOS)
        if not (inicio_ok <= ci <= fim_ok):
            alertas.append("checkin_fora_da_janela")
        if co is not None and minutos_entre(ci, co) > PERMANENCIA_MAXIMA_MINUTOS:
            alertas.append("permanencia_excedida")
        if co is None and agora - ci > timedelta(minutes=PERMANENCIA_MAXIMA_MINUTOS):
            alertas.append("sem_checkout")

    return {
        "id_visita": visita.id,
        "data_hora": visita.data_hora.isoformat(),
        "status": visita.status,
        "situacao": situacao,
        "situacao_texto": SITUACOES[situacao],
        "qr_code": visita.qr_code,
        "visitante": {"id": visitante.id, "nome": visitante.nome, "tipo": visitante.tipo},
        "paciente": {"id": paciente.id, "nome": paciente.nome},
        "leito": dict_leito(leito),
        "checkin": _iso(ci),
        "checkin_origem": checkin.origem if checkin else None,
        "checkout": _iso(co),
        "checkout_origem": checkout.origem if checkout else None,
        "permanencia_minutos": minutos_entre(ci, co),
        "alertas": [{"codigo": a, "texto": ALERTAS[a]} for a in alertas],
    }


def _consulta_base(inicio, fim, id_paciente=None, id_leito=None):
    consulta = (
        db.session.query(Visita, Visitante, Paciente, Leito)
        .join(Visitante, Visita.id_visitante == Visitante.id)
        .join(Internacao, Visita.id_internacao == Internacao.id)
        .join(Paciente, Internacao.id_paciente == Paciente.id)
        .join(Leito, Internacao.id_leito == Leito.id)
        .filter(Visita.data_hora >= inicio, Visita.data_hora <= fim)
    )
    if id_paciente:
        consulta = consulta.filter(Paciente.id == id_paciente)
    if id_leito:
        consulta = consulta.filter(Leito.id == id_leito)
    return consulta


def _montar_linhas(linhas):
    registros = registros_por_visita([l[0].id for l in linhas])
    agora = datetime.now()
    return [
        _linha(v, vis, p, l, registros[v.id]["checkin"], registros[v.id]["checkout"], agora)
        for v, vis, p, l in linhas
    ]


class AcessoService:

    # Check-in / Check-out (alimentam a auditoria - requisito 9)
    @staticmethod
    def registrar_checkin(id_visita, origem="recepcao"):
        from repositories.paciente_repository import PacienteRepository
        from services.vinculo.vinculo_service import VinculoService

        visita = Visita.query.get(id_visita)
        if visita is None:
            raise NaoEncontrado("Visita não encontrada.")
        if not visita.status:
            raise Conflito("Visita cancelada: o check-in não pode ser registrado.")
        existente = registros_por_visita([visita.id])[visita.id]["checkin"]
        if existente is not None:
            raise Conflito(f"Check-in já registrado em {existente.data_hora.strftime('%d/%m/%Y %H:%M')}.")
        if VinculoService.acesso_revogado(visita.id_visitante, visita.id_internacao):
            raise Proibido("O acesso deste visitante a este paciente foi revogado.")

        internacao = Internacao.query.get(visita.id_internacao)
        if internacao is not None:
            bloqueio = PacienteRepository.sp_verificar_bloqueio_status_paciente(internacao.id_paciente)
            if bloqueio["bloqueado"]:
                raise Proibido(bloqueio["motivo"])

        registro = RegistroAcesso(id_visita=visita.id, tipo=RegistroAcesso.TIPO_CHECKIN,
                                  data_hora=datetime.now(), origem=origem)
        registro.salvar()
        return registro.to_dict()

    @staticmethod
    def registrar_checkout(id_visita, origem="recepcao"):
        visita = Visita.query.get(id_visita)
        if visita is None:
            raise NaoEncontrado("Visita não encontrada.")
        registros = registros_por_visita([visita.id])[visita.id]
        if registros["checkin"] is None:
            raise Conflito("Não há check-in registrado para esta visita.")
        if registros["checkout"] is not None:
            raise Conflito(f"Check-out já registrado em {registros['checkout'].data_hora.strftime('%d/%m/%Y %H:%M')}.")

        registro = RegistroAcesso(id_visita=visita.id, tipo=RegistroAcesso.TIPO_CHECKOUT,
                                  data_hora=datetime.now(), origem=origem)
        registro.salvar()
        resposta = registro.to_dict()
        resposta["permanencia_minutos"] = minutos_entre(registros["checkin"].data_hora, registro.data_hora)
        return resposta

    @staticmethod
    def registrar_checkin_automatico(id_visita, origem="totem"):
        """Usado pelo totem: registra a entrada uma unica vez, sem interromper o fluxo se ja existir."""
        try:
            return AcessoService.registrar_checkin(id_visita, origem=origem)
        except (Conflito, Proibido, NaoEncontrado):
            return None

    # Requisito 8 - Relatorio de historico de visitas
    @staticmethod
    def historico_visitas(id_paciente=None, data_inicio=None, data_fim=None):
        if id_paciente and Paciente.query.get(id_paciente) is None:
            raise NaoEncontrado("Paciente não encontrado.")
        inicio, fim = parse_periodo(data_inicio, data_fim, dias_padrao=90)
        linhas = _consulta_base(inicio, fim, id_paciente=id_paciente).order_by(Visita.data_hora.desc()).all()
        visitas = _montar_linhas(linhas)

        resumo = {"total": len(visitas)}
        for chave in SITUACOES:
            resumo[chave] = sum(1 for v in visitas if v["situacao"] == chave)
        return {
            "periodo": {"inicio": inicio.isoformat(), "fim": fim.isoformat()},
            "id_paciente": id_paciente,
            "resumo": resumo,
            "visitas": visitas,
        }

    # Requisito 9 - Auditoria de check-in e check-out
    @staticmethod
    def auditoria_acessos(periodo_inicio=None, periodo_fim=None, id_leito=None, id_paciente=None):
        inicio, fim = parse_periodo(periodo_inicio, periodo_fim, dias_padrao=30)
        linhas = (
            _consulta_base(inicio, fim, id_paciente=id_paciente, id_leito=id_leito)
            .filter(Visita.status == True)  # noqa: E712
            .order_by(Visita.data_hora.desc())
            .all()
        )
        registros = _montar_linhas(linhas)
        com_checkin = [r for r in registros if r["checkin"]]
        permanencias = [r["permanencia_minutos"] for r in registros if r["permanencia_minutos"] is not None]
        resumo = {
            "total_visitas": len(registros),
            "total_checkins": len(com_checkin),
            "total_checkouts": sum(1 for r in registros if r["checkout"]),
            "sem_checkout": sum(1 for r in com_checkin if not r["checkout"]),
            "nao_compareceram": sum(1 for r in registros if r["situacao"] == "nao_compareceu"),
            "com_alerta": sum(1 for r in registros if r["alertas"]),
            "permanencia_media_minutos": round(sum(permanencias) / len(permanencias)) if permanencias else None,
        }
        return {
            "periodo": {"inicio": inicio.isoformat(), "fim": fim.isoformat()},
            "resumo": resumo,
            "registros": registros,
        }

    # Requisito 10 - Estatistica de visitantes por turno
    @staticmethod
    def visitantes_por_turno(periodo_inicio=None, periodo_fim=None):
        inicio, fim = parse_periodo(periodo_inicio, periodo_fim, dias_padrao=30)
        visitas = Visita.query.filter(Visita.data_hora >= inicio, Visita.data_hora <= fim).all()
        registros = registros_por_visita([v.id for v in visitas])

        dados = {nome: {"total": 0, "unicos": set(), "checkins": 0, "canceladas": 0} for nome, _, _ in TURNOS}
        todos_unicos = set()
        for v in visitas:
            turno = next(nome for nome, ini, fim_t in TURNOS if ini <= v.data_hora.hour < fim_t)
            if not v.status:
                dados[turno]["canceladas"] += 1
                continue
            dados[turno]["total"] += 1
            dados[turno]["unicos"].add(v.id_visitante)
            todos_unicos.add(v.id_visitante)
            if registros[v.id]["checkin"] is not None:
                dados[turno]["checkins"] += 1

        turnos = [{
            "turno": nome,
            "faixa": f"{ini:02d}:00 - {fim_t % 24:02d}:00",
            "total_visitantes": dados[nome]["total"],
            "visitantes_unicos": len(dados[nome]["unicos"]),
            "checkins": dados[nome]["checkins"],
            "canceladas": dados[nome]["canceladas"],
        } for nome, ini, fim_t in TURNOS]

        return {
            "periodo": {"inicio": inicio.isoformat(), "fim": fim.isoformat()},
            "turnos": turnos,
            "total_geral": {
                "total_visitantes": sum(t["total_visitantes"] for t in turnos),
                "visitantes_unicos": len(todos_unicos),
                "checkins": sum(t["checkins"] for t in turnos),
                "canceladas": sum(t["canceladas"] for t in turnos),
            },
        }
