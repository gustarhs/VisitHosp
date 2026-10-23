from datetime import datetime, timedelta

from extensions import db
from models import Visita, Visitante, Internacao
from services.comum import (
    NaoEncontrado, Invalido, Conflito, SLOTS_PADRAO, CAPACIDADE_MAXIMA_POR_HORARIO,
    ANTECEDENCIA_MINIMA_ALTERACAO_MINUTOS, parse_data, registros_por_visita,
    situacao_visita, pode_alterar, inicio_do_slot, contar_ocupacao, SITUACOES,
)


def _item(visita, visitante, checkin, checkout, agora):
    situacao = situacao_visita(visita, checkin, checkout, agora)
    return {
        "id": visita.id,
        "data_hora": visita.data_hora.isoformat(),
        "status": visita.status,
        "situacao": situacao,
        "situacao_texto": SITUACOES[situacao],
        "qr_code": visita.qr_code,
        "id_internacao": visita.id_internacao,
        "visitante": {"id": visitante.id, "nome": visitante.nome} if visitante else None,
        "pode_alterar": pode_alterar(visita, checkin, agora),
    }


def _validar_alteravel(visita, acao):
    if not visita.status:
        raise Conflito("Este agendamento já está cancelado." if acao == "cancelar"
                       else "Agendamento cancelado não pode ser alterado.")
    if registros_por_visita([visita.id])[visita.id]["checkin"] is not None:
        raise Conflito(f"Não é possível {acao}: a entrada (check-in) já foi registrada.")
    if visita.data_hora - datetime.now() < timedelta(minutes=ANTECEDENCIA_MINIMA_ALTERACAO_MINUTOS):
        raise Conflito(f"Só é possível {acao} com no mínimo {ANTECEDENCIA_MINIMA_ALTERACAO_MINUTOS} "
                       "minutos de antecedência.")


class AgendamentoService:

    @staticmethod
    def listar_por_internacao(id_internacao, id_visitante=None):
        if Internacao.query.get(id_internacao) is None:
            raise NaoEncontrado("Internação não encontrada.")
        consulta = (
            db.session.query(Visita, Visitante)
            .join(Visitante, Visita.id_visitante == Visitante.id)
            .filter(Visita.id_internacao == id_internacao)
        )
        if id_visitante:
            consulta = consulta.filter(Visita.id_visitante == id_visitante)
        linhas = consulta.order_by(Visita.data_hora.desc()).all()
        registros = registros_por_visita([v.id for v, _ in linhas])
        agora = datetime.now()
        return [_item(v, vis, registros[v.id]["checkin"], registros[v.id]["checkout"], agora) for v, vis in linhas]

    # Requisito 5 - Cancelar agendamento
    @staticmethod
    def cancelar(id_visita):
        visita = Visita.query.get(id_visita)
        if visita is None:
            raise NaoEncontrado("Agendamento não encontrado.")
        _validar_alteravel(visita, "cancelar")
        visita.status = False
        db.session.commit()
        return _item(visita, Visitante.query.get(visita.id_visitante), None, None, datetime.now())

    # Requisito 5 - Alterar (reagendar) agendamento
    @staticmethod
    def reagendar(id_visita, nova_data_hora_str):
        visita = Visita.query.get(id_visita)
        if visita is None:
            raise NaoEncontrado("Agendamento não encontrado.")
        _validar_alteravel(visita, "alterar")

        nova = parse_data(nova_data_hora_str, "data_hora")
        agora = datetime.now()
        if nova.strftime("%H:%M") not in {ini for ini, _ in SLOTS_PADRAO} or nova.second != 0:
            raise Invalido("Escolha um dos horários oficiais de visita (ex.: 09:00, 09:30, 14:00...).")
        if nova <= agora:
            raise Invalido("O novo horário precisa estar no futuro.")
        if nova == visita.data_hora:
            raise Invalido("O novo horário é igual ao horário atual do agendamento.")

        internacao = Internacao.query.get(visita.id_internacao)
        if internacao is None:
            raise NaoEncontrado("Internação do agendamento não encontrada.")
        if not internacao.status:
            raise Conflito("A internação deste paciente não está mais ativa.")

        ini, fim = inicio_do_slot(nova)
        if contar_ocupacao(internacao.id_leito, ini, fim, ignorar_visita=visita.id) >= CAPACIDADE_MAXIMA_POR_HORARIO:
            raise Conflito("Este horário está lotado para o leito. Escolha outro horário.")

        duplicada = Visita.query.filter(
            Visita.id != visita.id,
            Visita.id_visitante == visita.id_visitante,
            Visita.status == True,  # noqa: E712
            Visita.data_hora == nova,
        ).first()
        if duplicada:
            raise Conflito("O visitante já possui outro agendamento neste mesmo horário.")

        visita.data_hora = nova
        db.session.commit()
        return _item(visita, Visitante.query.get(visita.id_visitante), None, None, agora)
