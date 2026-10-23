from datetime import datetime, timedelta
from urllib.parse import quote_plus

from models import Hospital, Paciente, Internacao, Leito, Visita
from repositories.visitante_repository import VisitanteRepository
from services.comum import (
    NaoEncontrado, Invalido, SLOTS_PADRAO, CAPACIDADE_MAXIMA_POR_HORARIO,
    DURACAO_SLOT_MINUTOS, JANELA_CHECKIN_ANTES_MINUTOS, JANELA_CHECKIN_DEPOIS_MINUTOS,
    PERMANENCIA_MAXIMA_MINUTOS, ANTECEDENCIA_MINIMA_ALTERACAO_MINUTOS,
    contar_ocupacao, dict_leito,
)


def _endereco(hospital):
    if hospital is None:
        return None
    return f"{hospital.rua}, {hospital.numero} - {hospital.cidade}/{hospital.estado}"


def _janelas_oficiais():
    """Agrupa os horarios padrao em janelas continuas (ex.: 09:00-11:00 e 14:00-16:00)."""
    janelas, atual = [], None
    for inicio, fim in SLOTS_PADRAO:
        if atual and atual["fim"] == inicio:
            atual["fim"] = fim
            atual["quantidade_horarios"] += 1
        else:
            if atual:
                janelas.append(atual)
            atual = {"inicio": inicio, "fim": fim, "quantidade_horarios": 1}
    if atual:
        janelas.append(atual)
    for j in janelas:
        j["periodo"] = "Manhã" if int(j["inicio"][:2]) < 12 else "Tarde"
    return janelas


class ConsultaService:

    # Requisito 1 - Regulamento e horarios oficiais
    @staticmethod
    def obter_regulamento():
        hospital = Hospital.query.first()
        regras = [
            {"titulo": "Horários de visita",
             "descricao": "As visitas acontecem somente nos horários oficiais, em blocos de "
                          f"{DURACAO_SLOT_MINUTOS} minutos, mediante agendamento prévio."},
            {"titulo": "Capacidade por horário",
             "descricao": f"Cada horário comporta no máximo {CAPACIDADE_MAXIMA_POR_HORARIO} visitantes "
                          "simultâneos por leito."},
            {"titulo": "Duração máxima",
             "descricao": f"A permanência não deve ultrapassar {PERMANENCIA_MAXIMA_MINUTOS} minutos por visita."},
            {"titulo": "Triagem sanitária",
             "descricao": "É obrigatório responder à triagem digital antes de cada visita. "
                          "Quem apresentar sintomas ou critérios de risco fica impedido de visitar."},
            {"titulo": "QR Code e check-in",
             "descricao": f"A entrada é feita com o QR Code da visita, liberada de {JANELA_CHECKIN_ANTES_MINUTOS} "
                          f"minutos antes até {JANELA_CHECKIN_DEPOIS_MINUTOS} minutos depois do horário agendado. "
                          "Entrada e saída são registradas para auditoria."},
            {"titulo": "Alteração e cancelamento",
             "descricao": f"O agendamento pode ser alterado ou cancelado com no mínimo "
                          f"{ANTECEDENCIA_MINIMA_ALTERACAO_MINUTOS} minutos de antecedência."},
            {"titulo": "Cadastro e vínculo",
             "descricao": "Todo visitante deve estar cadastrado e vinculado ao paciente e ao leito. "
                          "O acesso pode ser revogado a qualquer momento."},
            {"titulo": "Restrições clínicas",
             "descricao": "Pacientes em isolamento, procedimento ou estado crítico podem ter as visitas "
                          "temporariamente suspensas pela equipe de enfermagem."},
            {"titulo": "Privacidade (LGPD)",
             "descricao": "Os dados do paciente só são exibidos mediante token de acesso e os dados "
                          "pessoais são tratados conforme a LGPD."},
        ]
        return {
            "hospital": None if hospital is None else {
                "nome": hospital.nome,
                "endereco": _endereco(hospital),
                "horario_inicio_visitas": hospital.horario_visita.strftime("%H:%M"),
            },
            "horarios_oficiais": _janelas_oficiais(),
            "horarios": [{"inicio": i, "fim": f} for i, f in SLOTS_PADRAO],
            "duracao_slot_minutos": DURACAO_SLOT_MINUTOS,
            "capacidade_por_horario": CAPACIDADE_MAXIMA_POR_HORARIO,
            "permanencia_maxima_minutos": PERMANENCIA_MAXIMA_MINUTOS,
            "regras": regras,
            "regras_por_papel": VisitanteRepository.REGRAS_POR_PAPEL,
        }

    # Requisito 2 - Status do paciente
    @staticmethod
    def status_paciente(id_paciente):
        paciente = Paciente.query.get(id_paciente)
        if paciente is None:
            raise NaoEncontrado("Paciente não encontrado.")

        internacao = (
            Internacao.query.filter_by(id_paciente=id_paciente, status=True)
            .order_by(Internacao.id.desc()).first()
        )
        leito = Leito.query.get(internacao.id_leito) if internacao else None

        # Convencao do projeto (PacienteRepository): paciente.status True = visitas restritas
        restrito = paciente.status is True

        if internacao is None:
            situacao, liberado = "sem_internacao", False
            mensagem = "Paciente sem internação ativa (alta registrada). Novas visitas não são permitidas."
        elif restrito:
            situacao, liberado = "restrito", False
            mensagem = "Visitas temporariamente suspensas (isolamento, procedimento ou estado crítico)."
        else:
            situacao, liberado = "liberado", True
            mensagem = "Paciente disponível para visitas nos horários oficiais."

        visitas_hoje = 0
        if internacao is not None:
            inicio = datetime.combine(datetime.now().date(), datetime.min.time())
            visitas_hoje = Visita.query.filter(
                Visita.id_internacao == internacao.id,
                Visita.status == True,  # noqa: E712
                Visita.data_hora >= inicio,
                Visita.data_hora < inicio + timedelta(days=1),
            ).count()

        return {
            "id_paciente": paciente.id,
            "nome": paciente.nome,
            "situacao": situacao,
            "liberado_para_visitas": liberado,
            "mensagem": mensagem,
            "internacao": None if internacao is None else {
                "id": internacao.id,
                "data_entrada": internacao.data_entrada.isoformat(),
                "data_saida_prevista": internacao.data_saida.isoformat(),
            },
            "leito": dict_leito(leito),
            "visitas_agendadas_hoje": visitas_hoje,
            "consultado_em": datetime.now().isoformat(timespec="seconds"),
        }

    # Requisito 3 - Orientacoes de localizacao do leito
    @staticmethod
    def localizacao_leito(id_leito):
        leito = Leito.query.get(id_leito)
        if leito is None:
            raise NaoEncontrado("Leito não encontrado.")
        hospital = Hospital.query.first()

        andar_txt = "térreo" if leito.andar == 0 else f"{leito.andar}º andar"
        if hospital is not None:
            passos = [f"Dirija-se à entrada principal do {hospital.nome} ({_endereco(hospital)})."]
        else:
            passos = ["Dirija-se à entrada principal do hospital."]
        passos += [
            "Identifique-se na recepção com o QR Code da sua visita.",
            f"Siga para o Bloco {leito.bloco}.",
            f"Use o elevador ou a escada até o {andar_txt}." if leito.andar else "O acesso é no térreo, sem necessidade de elevador.",
            f"Procure a ala {leito.ala}.",
            f"Localize o leito/quarto {leito.numero} e higienize as mãos antes de entrar.",
        ]

        mapa_url = None
        if hospital is not None:
            mapa_url = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(
                f"{hospital.nome}, {hospital.rua}, {hospital.numero}, {hospital.cidade}, {hospital.estado}"
            )

        return {
            "leito": dict_leito(leito),
            "resumo": f"Bloco {leito.bloco} • {andar_txt} • Ala {leito.ala} • Leito {leito.numero}",
            "hospital": None if hospital is None else {"nome": hospital.nome, "endereco": _endereco(hospital)},
            "orientacoes": passos,
            "mapa_url": mapa_url,
        }

    # Requisito 6 - Horarios ocupados do mesmo leito
    @staticmethod
    def horarios_ocupados_leito(id_leito, data_str=None):
        leito = Leito.query.get(id_leito)
        if leito is None:
            raise NaoEncontrado("Leito não encontrado.")
        if data_str:
            try:
                data = datetime.strptime(data_str, "%Y-%m-%d").date()
            except ValueError:
                raise Invalido("Parâmetro 'data' inválido. Use o formato YYYY-MM-DD.")
        else:
            data = datetime.now().date()

        horarios = []
        for ini_str, fim_str in SLOTS_PADRAO:
            inicio = datetime.combine(data, datetime.strptime(ini_str, "%H:%M").time())
            fim = datetime.combine(data, datetime.strptime(fim_str, "%H:%M").time())
            ocupacao = contar_ocupacao(id_leito, inicio, fim)
            if ocupacao >= CAPACIDADE_MAXIMA_POR_HORARIO:
                situacao = "lotado"
            elif ocupacao > 0:
                situacao = "parcial"
            else:
                situacao = "livre"
            horarios.append({
                "horario": f"{ini_str} - {fim_str}",
                "inicio": inicio.isoformat(),
                "ocupacao": ocupacao,
                "capacidade": CAPACIDADE_MAXIMA_POR_HORARIO,
                "vagas": max(CAPACIDADE_MAXIMA_POR_HORARIO - ocupacao, 0),
                "situacao": situacao,
            })

        return {
            "id_leito": leito.id,
            "leito": dict_leito(leito),
            "data": data.isoformat(),
            "capacidade": CAPACIDADE_MAXIMA_POR_HORARIO,
            "horarios": horarios,
            "ocupados": [h for h in horarios if h["ocupacao"] > 0],
        }
