from datetime import datetime, timedelta

from sqlalchemy import func

from extensions import db
from models.visita import Visita
from models.visitante import Visitante
from models.internacao import Internacao
from models.paciente import Paciente
from models.leito import Leito


class VisitaRepository:
    """
    Camada de repository para o agregado Visita.

    ATENCAO - limitacoes do schema atual (nenhuma alteracao de banco foi feita):
    - A tabela visita possui apenas um campo de data/hora (data_hora),
      usado tanto como horario agendado quanto, quando a visita e
      confirmada no totem, como o proprio horario de entrada. Nao existe um
      campo separado de horario de saida, entao o calculo exato de "tempo de
      permanencia" (conforme o requisito de auditoria de fluxo) nao pode ser
      feito. O relatorio de auditoria abaixo foi adaptado para o que e
      calculavel com os dados existentes (volume de visitas por leito no
      periodo); para ter o calculo de duracao real, seria necessario um
      campo adicional (ex.: horario_saida), o que nao foi feito por
      respeitar a restricao de nao alterar o banco.
    - Nao existe tabela de configuracao para "janela de liberacao do QR
      Code" nem "duracao maxima permitida"; esses valores ficam como
      constantes de negocio no codigo.
    """

    DURACAO_SLOT_MINUTOS = 30
    JANELA_QRCODE_MINUTOS = 20
    DURACAO_MAXIMA_PERMITIDA_MINUTOS = 60

    @staticmethod
    def sp_historico_visitas_paciente(id_paciente, data_inicio=None, data_fim=None):
        """
        sp_historico_visitas_paciente(id_paciente, data_inicio, data_fim)

        Logica:
            1. JOIN visita -> internacao (para chegar ao paciente) e
               visita -> visitante (para o nome do visitante).
            2. Filtra (WHERE) por id_paciente e, se informado, pelo
               intervalo de datas.
            3. Ordena por data/horario decrescente (ORDER BY data_hora DESC).

        Retorno: lista de visitas com nome do visitante, data, horario e
        status.
        """
        query = (
            db.session.query(Visita, Visitante)
            .join(Internacao, Visita.id_internacao == Internacao.id)
            .join(Visitante, Visita.id_visitante == Visitante.id)
            .filter(Internacao.id_paciente == id_paciente)
        )

        if data_inicio:
            query = query.filter(Visita.data_hora >= data_inicio)
        if data_fim:
            query = query.filter(Visita.data_hora <= data_fim)

        resultados = query.order_by(Visita.data_hora.desc()).all()

        return [
            {
                "visitante": visitante.nome,
                "data_hora": visita.data_hora.isoformat(),
                "status": visita.status,
                "qr_code": visita.qr_code,
            }
            for visita, visitante in resultados
        ]

    @staticmethod
    def sp_relatorio_auditoria_fluxo(id_leito=None, periodo_inicio=None, periodo_fim=None):
        """
        sp_relatorio_auditoria_fluxo(id_leito, periodo_inicio, periodo_fim)

        Logica (adaptada - ver observacao da classe sobre a ausencia de
        horario de saida no schema atual):
            1. Filtra visitas confirmadas (status=True) dentro do periodo.
            2. Se id_leito informado, filtra tambem por leito (via
               internacao).
            3. Agrupa (GROUP BY) por leito para contar o total de visitas.
            4. Ordena pelo total de visitas (ORDER BY total DESC), como
               proxy de possiveis gargalos de fluxo.

        Retorno: relatorio por leito com o total de visitas no periodo.
        """
        query = (
            db.session.query(
                Internacao.id_leito,
                func.count(Visita.id).label("total_visitas"),
            )
            .join(Internacao, Visita.id_internacao == Internacao.id)
            .filter(
                Visita.status == True,  # noqa: E712
                Visita.data_hora >= periodo_inicio,
                Visita.data_hora <= periodo_fim,
            )
        )

        if id_leito:
            query = query.filter(Internacao.id_leito == id_leito)

        resultados = (
            query.group_by(Internacao.id_leito)
            .order_by(func.count(Visita.id).desc())
            .all()
        )

        return [
            {"id_leito": leito_id, "total_visitas": total}
            for leito_id, total in resultados
        ]

    @staticmethod
    def sp_relatorio_gerencial_visitas(periodo_inicio, periodo_fim, id_paciente=None):
        """
        sp_relatorio_gerencial_visitas(periodo_inicio, periodo_fim, id_paciente)

        Logica:
            1. Filtra visitas dentro do periodo informado
               (WHERE data BETWEEN ...).
            2. Se id_paciente informado, filtra tambem por ele; senao,
               considera todos.
            3. Agrupa (GROUP BY paciente) e conta (COUNT) o total de visitas.

        Retorno: tabela consolidada com paciente, total de visitas no
        periodo.
        """
        query = (
            db.session.query(
                Paciente.id,
                Paciente.nome,
                func.count(Visita.id).label("total_visitas"),
            )
            .join(Internacao, Internacao.id_paciente == Paciente.id)
            .join(Visita, Visita.id_internacao == Internacao.id)
            .filter(
                Visita.data_hora >= periodo_inicio,
                Visita.data_hora <= periodo_fim,
            )
        )

        if id_paciente:
            query = query.filter(Paciente.id == id_paciente)

        resultados = (
            query.group_by(Paciente.id, Paciente.nome)
            .order_by(func.count(Visita.id).desc())
            .all()
        )

        return [
            {"id_paciente": pid, "nome": nome, "total_visitas": total}
            for pid, nome, total in resultados
        ]

    @staticmethod
    def sp_verificar_slot_extensao(id_leito, horario_agendado):
        """
        sp_verificar_slot_extensao(id_leito, horario_agendado)

        Logica:
            1. Calcula o slot imediatamente seguinte
               (horario_agendado + duracao_do_slot).
            2. Verifica (WHERE NOT EXISTS) se existe reserva ativa para
               aquele leito nesse proximo slot.

        Retorno: bool - True (disponivel_para_extensao) se o proximo slot
        estiver livre, disparando a oferta automatica de extensao.
        """
        proximo_slot_inicio = horario_agendado + timedelta(minutes=VisitaRepository.DURACAO_SLOT_MINUTOS)
        proximo_slot_fim = proximo_slot_inicio + timedelta(minutes=VisitaRepository.DURACAO_SLOT_MINUTOS)

        existe_reserva = (
            db.session.query(Visita.id)
            .join(Internacao, Visita.id_internacao == Internacao.id)
            .filter(
                Internacao.id_leito == id_leito,
                Visita.status == True,  # noqa: E712
                Visita.data_hora >= proximo_slot_inicio,
                Visita.data_hora < proximo_slot_fim,
            )
            .first()
        )

        return existe_reserva is None

    @staticmethod
    def sp_validar_janela_qrcode(id_visita):
        """
        sp_validar_janela_qrcode(id_agendamento)

        Parametros de entrada: id_visita (o "agendamento" e a propria
        visita, pois nao existe uma tabela separada de agendamentos).

        Logica:
            1. Busca o horario agendado da visita.
            2. Calcula a janela de liberacao
               (horario_agendado - JANELA_QRCODE_MINUTOS).
            3. Compara com o horario atual.

        Retorno: bool - pode_gerar_qrcode.
        """
        visita = Visita.query.get(id_visita)
        if visita is None:
            raise ValueError(f"Visita {id_visita} nao encontrada.")

        agora = datetime.now()
        janela_inicio = visita.data_hora - timedelta(minutes=VisitaRepository.JANELA_QRCODE_MINUTOS)

        return janela_inicio <= agora <= visita.data_hora

    @staticmethod
    def sp_validar_entrada_totem(codigo_qrcode):
        """
        sp_validar_entrada_totem(codigo_qrcode)

        Logica:
            1. Busca a visita pelo QR Code, validando que esta ativa
               (WHERE qr_code = ? AND status = 'ativo').
            2. JOIN com visitante, internacao, paciente e leito para
               confirmar identidade e montar os dados de notificacao.
            3. Reaproveita a checagem de bloqueio por status critico do
               paciente (PacienteRepository.sp_verificar_bloqueio_status_paciente)
               antes de liberar a entrada.
            4. Se tudo valido, marca a visita como presente (status=True) e
               retorna os dados para notificacao da enfermagem.

        Retorno: dict com confirmacao/motivo de negacao + dados para
        notificacao/impressao da etiqueta.
        """
        # import local para evitar import circular entre repositories
        from repositories.paciente_repository import PacienteRepository

        visita = Visita.query.filter_by(qr_code=codigo_qrcode).first()
        if visita is None:
            return {"liberado": False, "motivo": "QR Code nao encontrado."}

        if not visita.status:
            return {"liberado": False, "motivo": "QR Code invalido ou ja utilizado."}

        internacao = Internacao.query.get(visita.id_internacao) if visita.id_internacao else None
        if internacao is None:
            return {"liberado": False, "motivo": "Internacao vinculada nao encontrada."}

        bloqueio = PacienteRepository.sp_verificar_bloqueio_status_paciente(internacao.id_paciente)
        if bloqueio["bloqueado"]:
            return {"liberado": False, "motivo": bloqueio["motivo"]}

        visitante = Visitante.query.get(visita.id_visitante)
        leito = Leito.query.get(internacao.id_leito)

        visita.status = True
        db.session.commit()

        return {
            "liberado": True,
            "notificacao": {
                "visitante": visitante.nome if visitante else None,
                "leito": leito.to_dict() if leito else None,
            },
        }