from datetime import datetime

from extensions import db
from models import Visitante, Paciente, Leito, Internacao, Visita, VisitanteVinculo
from services.comum import (
    Invalido, NaoEncontrado, Conflito, Proibido, registros_por_visita, dict_leito,
)

TIPOS_PERMITIDOS = {"visitante", "acompanhante", "ADM1", "ADM2"}


def somente_digitos(cpf):
    return "".join(c for c in str(cpf or "") if c.isdigit())


def cpf_valido(cpf):
    d = somente_digitos(cpf)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for i in (9, 10):
        soma = sum(int(d[j]) * (i + 1 - j) for j in range(i))
        if (soma * 10 % 11) % 10 != int(d[i]):
            return False
    return True


def formatar_cpf(d):
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def mascarar_cpf(cpf):
    d = somente_digitos(cpf)
    return f"***.{d[3:6]}.{d[6:9]}-**" if len(d) == 11 else "***"


class VinculoService:

    # Requisito 7 - Cadastro de visitante com vinculo a paciente e leito
    @staticmethod
    def cadastrar_visitante_vinculado(dados):
        dados = dados or {}
        obrigatorios = ["nome", "cpf", "data_nascimento", "tipo", "id_paciente", "id_leito"]
        faltando = [c for c in obrigatorios if dados.get(c) in (None, "")]
        if faltando:
            raise Invalido(f"Campos obrigatórios faltando: {', '.join(faltando)}")

        nome = str(dados["nome"]).strip()
        if len(nome) < 3:
            raise Invalido("Informe o nome completo do visitante.")
        if not cpf_valido(dados["cpf"]):
            raise Invalido("CPF inválido.")
        cpf_digitos = somente_digitos(dados["cpf"])

        try:
            nascimento = datetime.fromisoformat(str(dados["data_nascimento"]).strip().replace("Z", ""))
        except ValueError:
            raise Invalido("data_nascimento inválida. Use o formato YYYY-MM-DD.")
        if nascimento > datetime.now():
            raise Invalido("A data de nascimento não pode estar no futuro.")
        if dados["tipo"] not in TIPOS_PERMITIDOS:
            raise Invalido(f"Tipo inválido. Use um destes: {', '.join(sorted(TIPOS_PERMITIDOS))}.")
        if dados.get("termo_consentimento") is not True:
            raise Invalido("É necessário aceitar o termo de consentimento (LGPD).")

        paciente = Paciente.query.get(dados["id_paciente"])
        if paciente is None:
            raise NaoEncontrado("Paciente não encontrado.")
        leito = Leito.query.get(dados["id_leito"])
        if leito is None:
            raise NaoEncontrado("Leito não encontrado.")

        internacao = (
            Internacao.query.filter_by(id_paciente=paciente.id, id_leito=leito.id, status=True)
            .order_by(Internacao.id.desc()).first()
        )
        if internacao is None:
            raise Invalido("Não há internação ativa deste paciente neste leito.")

        # Reaproveita o visitante se o CPF ja existir (formatado ou so digitos)
        visitante = Visitante.query.filter(
            Visitante.cpf.in_([cpf_digitos, formatar_cpf(cpf_digitos)])
        ).first()
        reutilizado = visitante is not None

        if visitante is not None:
            anteriores = VisitanteVinculo.query.filter_by(id_visitante=visitante.id, id_paciente=paciente.id).all()
            if any(v.ativo for v in anteriores):
                raise Conflito("Este visitante já está vinculado a este paciente.")
            if anteriores:
                raise Proibido("O acesso deste visitante a este paciente foi revogado. "
                               "Procure a equipe de enfermagem.")
        else:
            visitante = Visitante(status=True, tipo=dados["tipo"], nome=nome, data_nascimento=nascimento,
                                  termo_consentimento=True, cpf=cpf_digitos)
            db.session.add(visitante)
            db.session.flush()

        parentesco = str(dados.get("parentesco") or "").strip() or None
        vinculo = VisitanteVinculo(
            id_visitante=visitante.id, id_paciente=paciente.id, id_leito=leito.id,
            id_internacao=internacao.id, parentesco=parentesco, ativo=True, criado_em=datetime.now(),
        )
        db.session.add(vinculo)
        db.session.commit()

        return {
            "visitante": visitante.to_dict(),
            "vinculo": vinculo.to_dict(),
            "paciente": {"id": paciente.id, "nome": paciente.nome},
            "leito": dict_leito(leito),
            "reutilizado": reutilizado,
        }

    @staticmethod
    def listar_vinculos_paciente(id_paciente):
        if Paciente.query.get(id_paciente) is None:
            raise NaoEncontrado("Paciente não encontrado.")
        linhas = (
            db.session.query(VisitanteVinculo, Visitante, Leito)
            .join(Visitante, VisitanteVinculo.id_visitante == Visitante.id)
            .join(Leito, VisitanteVinculo.id_leito == Leito.id)
            .filter(VisitanteVinculo.id_paciente == id_paciente)
            .order_by(VisitanteVinculo.ativo.desc(), VisitanteVinculo.criado_em.desc())
            .all()
        )
        agora = datetime.now()
        resultado = []
        for vinc, vis, leito in linhas:
            futuras = Visita.query.join(Internacao, Visita.id_internacao == Internacao.id).filter(
                Visita.id_visitante == vis.id,
                Internacao.id_paciente == id_paciente,
                Visita.status == True,  # noqa: E712
                Visita.data_hora > agora,
            ).count()
            resultado.append({
                "id_vinculo": vinc.id,
                "id_visitante": vis.id,
                "nome": vis.nome,
                "cpf": mascarar_cpf(vis.cpf),
                "tipo": vis.tipo,
                "parentesco": vinc.parentesco,
                "leito": dict_leito(leito),
                "ativo": vinc.ativo,
                "criado_em": vinc.criado_em.isoformat() if vinc.criado_em else None,
                "revogado_em": vinc.revogado_em.isoformat() if vinc.revogado_em else None,
                "motivo_revogacao": vinc.motivo_revogacao,
                "visitas_futuras": futuras,
            })
        return resultado

    # Requisito 4 - Revogar acesso do visitante
    @staticmethod
    def revogar_acesso(id_visitante, id_paciente=None, motivo=None):
        visitante = Visitante.query.get(id_visitante)
        if visitante is None:
            raise NaoEncontrado("Visitante não encontrado.")
        motivo = (str(motivo).strip()[:255] or None) if motivo else None
        agora = datetime.now()

        consulta = VisitanteVinculo.query.filter_by(id_visitante=id_visitante)
        if id_paciente:
            if Paciente.query.get(id_paciente) is None:
                raise NaoEncontrado("Paciente não encontrado.")
            consulta = consulta.filter_by(id_paciente=id_paciente)
        vinculos = consulta.all()
        ativos = [v for v in vinculos if v.ativo]

        if not vinculos and id_paciente:
            # Visitante sem vinculo (cadastrado pela rota antiga): cria o vinculo ja revogado
            # para que ele seja barrado em novos agendamentos deste paciente.
            internacao = (
                Internacao.query.filter_by(id_paciente=id_paciente, status=True).order_by(Internacao.id.desc()).first()
                or Internacao.query.filter_by(id_paciente=id_paciente).order_by(Internacao.id.desc()).first()
            )
            if internacao is None:
                raise NaoEncontrado("Paciente sem internação registrada.")
            db.session.add(VisitanteVinculo(
                id_visitante=id_visitante, id_paciente=id_paciente, id_leito=internacao.id_leito,
                id_internacao=internacao.id, ativo=False, criado_em=agora,
                revogado_em=agora, motivo_revogacao=motivo,
            ))
            total_revogados = 1
        else:
            if not vinculos:
                raise NaoEncontrado("Este visitante não possui vínculo com nenhum paciente.")
            if not ativos:
                raise Conflito("O acesso deste visitante já foi revogado.")
            for v in ativos:
                v.ativo = False
                v.revogado_em = agora
                v.motivo_revogacao = motivo
            total_revogados = len(ativos)

        # Cancela as visitas futuras (ainda sem check-in) do visitante
        filtro = Visita.query.join(Internacao, Visita.id_internacao == Internacao.id).filter(
            Visita.id_visitante == id_visitante,
            Visita.status == True,  # noqa: E712
            Visita.data_hora > agora,
        )
        if id_paciente:
            filtro = filtro.filter(Internacao.id_paciente == id_paciente)
        futuras = filtro.all()
        registros = registros_por_visita([v.id for v in futuras])
        canceladas = 0
        for visita in futuras:
            if registros[visita.id]["checkin"] is None:
                visita.status = False
                canceladas += 1

        db.session.commit()
        return {
            "id_visitante": id_visitante,
            "nome": visitante.nome,
            "vinculos_revogados": total_revogados,
            "visitas_canceladas": canceladas,
            "revogado_em": agora.isoformat(timespec="seconds"),
        }

    @staticmethod
    def acesso_revogado(id_visitante, id_internacao):
        """True se o visitante teve o acesso ao paciente revogado e nao tem vinculo ativo."""
        internacao = Internacao.query.get(id_internacao)
        if internacao is None:
            return False
        vinculos = VisitanteVinculo.query.filter_by(
            id_visitante=id_visitante, id_paciente=internacao.id_paciente
        ).all()
        return bool(vinculos) and not any(v.ativo for v in vinculos)
