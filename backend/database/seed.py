"""
Dados de demonstracao do VisitHosp.
Executado automaticamente na primeira inicializacao (banco vazio) ou manualmente:
    python seed.py            -> popula somente se o banco estiver vazio
    python seed.py --reset    -> APAGA TODAS AS TABELAS e popula de novo
"""
import random
from datetime import datetime, timedelta

from extensions import db
from models import (
    Hospital, Leito, Paciente, Internacao, Visitante, Visita, VisitanteVinculo, RegistroAcesso,
)
from services.visita._helpers import SLOTS_PADRAO, CAPACIDADE_MAXIMA_POR_HORARIO


def _cpf(base9):
    """Gera um CPF valido a partir de 9 digitos."""
    d = [int(c) for c in base9]
    for i in (9, 10):
        soma = sum(d[j] * (i + 1 - j) for j in range(i))
        d.append((soma * 10 % 11) % 10)
    return "".join(str(x) for x in d)


def banco_vazio():
    return Hospital.query.count() == 0 and Paciente.query.count() == 0 and Visitante.query.count() == 0


def popular_banco():
    rnd = random.Random(42)
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    hospital = Hospital(nome="Hospital VisitHosp", horario_visita=datetime(2026, 1, 1, 14, 0),
                        rua="Avenida Brasil", numero="1000", cidade="Belo Horizonte", estado="MG")
    db.session.add(hospital)

    # Leitos (status True = ocupado)
    leitos_def = [
        (True, "Clínica Médica", 101, 1, "A"),
        (True, "Clínica Médica", 102, 1, "A"),
        (True, "UTI Adulto", 201, 2, "A"),
        (True, "Maternidade", 305, 3, "B"),
        (False, "Ortopedia", 410, 4, "B"),
        (False, "Pediatria", 112, 1, "C"),
    ]
    leitos = [Leito(status=s, ala=a, numero=n, andar=an, bloco=b) for s, a, n, an, b in leitos_def]
    db.session.add_all(leitos)

    # Pacientes (status True = visitas restritas, convencao do PacienteRepository)
    pacientes_def = [
        ("Carlos Eduardo Ribeiro", "1958-03-14", "adulto", False, _cpf("111444777")),
        ("Helena Martins Souza", "1971-11-02", "adulto", False, _cpf("222555888")),
        ("José Antônio Pereira", "1946-07-29", "idoso", True, _cpf("333666999")),
        ("Luciana Ferreira Lima", "1992-01-20", "adulto", False, _cpf("444777111")),
        ("Roberto Almeida Costa", "1980-09-08", "adulto", False, _cpf("555888222")),
    ]
    pacientes = [Paciente(nome=n, data_nascimento=datetime.fromisoformat(nasc), tipo=t, status=s, cpf=c)
                 for n, nasc, t, s, c in pacientes_def]
    db.session.add_all(pacientes)
    db.session.flush()

    # Internacoes (token no formato da tela de login: LNL-NLN-NLL)
    internacoes_def = [
        (0, 0, "A3F7K29MX", True, 6, 14),
        (1, 1, "B4C8D31PQ", True, 4, 10),
        (2, 2, "K9M2X70AB", True, 9, 20),
        (3, 3, "M2N4P85RT", True, 3, 7),
        (4, 4, "C5D1E47RS", False, 20, -2),  # alta: token invalido
    ]
    internacoes = []
    for ip, il, token, ativa, dias_atras, dias_saida in internacoes_def:
        internacoes.append(Internacao(
            data_entrada=(hoje - timedelta(days=dias_atras)).replace(hour=8),
            data_saida=(hoje + timedelta(days=dias_saida)).replace(hour=12),
            status=ativa, token_acesso=token,
            id_paciente=pacientes[ip].id, id_leito=leitos[il].id,
        ))
    db.session.add_all(internacoes)
    db.session.flush()

    # Visitantes + vinculos
    visitantes_def = [
        ("Maria Aparecida Santos", "1960-05-10", "visitante", _cpf("123456789"), 0, "Esposa"),
        ("Pedro Henrique Ribeiro", "1989-02-17", "acompanhante", _cpf("987654321"), 0, "Filho"),
        ("Ana Paula Martins", "1975-08-25", "visitante", _cpf("246813579"), 1, "Irmã"),
        ("Marcos Vinícius Souza", "1998-12-03", "visitante", _cpf("135792468"), 1, "Filho"),
        ("Fernanda Lopes Pereira", "1955-04-30", "ADM1", _cpf("112233445"), 2, "Esposa"),
        ("Ricardo Santos Lima", "1990-06-12", "visitante", _cpf("998877665"), 3, "Marido"),
    ]
    visitantes = []
    for nome, nasc, tipo, cpf, idx, parentesco in visitantes_def:
        v = Visitante(status=True, tipo=tipo, nome=nome, data_nascimento=datetime.fromisoformat(nasc),
                      termo_consentimento=True, cpf=cpf)
        db.session.add(v)
        db.session.flush()
        visitantes.append((v, idx))
        inter = internacoes[idx]
        db.session.add(VisitanteVinculo(
            id_visitante=v.id, id_paciente=inter.id_paciente, id_leito=inter.id_leito,
            id_internacao=inter.id, parentesco=parentesco, ativo=True,
            criado_em=inter.data_entrada + timedelta(hours=3),
        ))
    db.session.flush()

    # Visitas + check-in/check-out
    slots = [s[0] for s in SLOTS_PADRAO]
    ocupacao = {}
    contador = {"qr": 0}

    def criar_visita(visitante, internacao, data_hora, status=True):
        chave = (internacao.id, data_hora)
        if status and ocupacao.get(chave, 0) >= CAPACIDADE_MAXIMA_POR_HORARIO:
            return None
        contador["qr"] += 1
        visita = Visita(data_hora=data_hora, status=status, qr_code=f"VH-SEED-{contador['qr']:04d}",
                        id_visitante=visitante.id, id_hospital=hospital.id, id_internacao=internacao.id)
        db.session.add(visita)
        db.session.flush()
        if status:
            ocupacao[chave] = ocupacao.get(chave, 0) + 1
        return visita

    def registrar(visita, checkin_em, checkout_em=None):
        db.session.add(RegistroAcesso(id_visita=visita.id, tipo="checkin", data_hora=checkin_em, origem="totem"))
        if checkout_em:
            db.session.add(RegistroAcesso(id_visita=visita.id, tipo="checkout", data_hora=checkout_em, origem="recepcao"))

    compareceu = 0  # usado para gerar casos de auditoria
    for dias in range(12, 0, -1):
        dia = hoje - timedelta(days=dias)
        for visitante, idx in visitantes:
            internacao = internacoes[idx]
            if dia < internacao.data_entrada.replace(hour=0) or rnd.random() > 0.75:
                continue
            data_hora = datetime.combine(dia.date(), datetime.strptime(rnd.choice(slots), "%H:%M").time())
            if rnd.random() < 0.1:
                criar_visita(visitante, internacao, data_hora, status=False)  # cancelada
                continue
            visita = criar_visita(visitante, internacao, data_hora)
            if visita is None or rnd.random() < 0.12:
                continue  # nao compareceu

            compareceu += 1
            checkin = data_hora + timedelta(minutes=rnd.randint(-10, 15))
            permanencia = rnd.randint(20, 50)
            if compareceu == 3:      # check-in fora da janela
                checkin = data_hora + timedelta(minutes=55)
            elif compareceu == 6:    # permanencia acima do limite
                permanencia = 85
            elif compareceu == 9:    # saiu sem registrar check-out
                registrar(visita, checkin, None)
                continue
            registrar(visita, checkin, checkin + timedelta(minutes=permanencia))

    # Visitas futuras (mostram ocupacao do leito e permitem alterar/cancelar)
    amanha = hoje + timedelta(days=1)
    depois = hoje + timedelta(days=2)
    (v_maria, i_carlos), (v_pedro, _), (v_ana, i_helena) = visitantes[0], visitantes[1], visitantes[2]
    criar_visita(v_maria, internacoes[i_carlos], amanha.replace(hour=14))
    criar_visita(v_pedro, internacoes[i_carlos], amanha.replace(hour=14))
    criar_visita(v_maria, internacoes[i_carlos], depois.replace(hour=9, minute=30))
    criar_visita(v_ana, internacoes[i_helena], amanha.replace(hour=9))
    criar_visita(visitantes[3][0], internacoes[i_helena], amanha.replace(hour=15))
    criar_visita(visitantes[5][0], internacoes[3], depois.replace(hour=10))

    db.session.commit()
    return {
        "tokens": [(p.nome, i.token_acesso, i.status) for p, i in zip(pacientes, internacoes)],
        "visitas": Visita.query.count(),
    }


def imprimir_resumo(info):
    print("\n" + "=" * 70)
    print("BANCO POPULADO COM DADOS DE DEMONSTRAÇÃO")
    print("=" * 70)
    print(f"Visitas criadas: {info['visitas']}")
    print("Tokens de acesso para testar o login:")
    for nome, token, ativo in info["tokens"]:
        formatado = f"{token[:3]}-{token[3:6]}-{token[6:]}"
        print(f"  {formatado}   {nome}" + ("" if ativo else "   (internação encerrada - token inválido)"))
    print("=" * 70 + "\n")
