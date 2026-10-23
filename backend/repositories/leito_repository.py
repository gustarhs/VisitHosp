from datetime import datetime, timedelta

from sqlalchemy import func

from extensions import db
from models.leito import Leito
from models.hospital import Hospital
from models.internacao import Internacao
from models.visita import Visita


class LeitoRepository:
    """
    Camada de repository para o agregado Leito.

    ATENCAO - limitacoes do schema atual (nenhuma alteracao de banco foi feita):
    O schema nao possui uma tabela de configuracao com "duracao do slot" nem
    "capacidade maxima simultanea por leito/setor" (previstas no documento de
    requisitos). Esses dois valores ficam como constantes de negocio no
    codigo. Tambem nao existe FK entre leito e hospital, entao usamos o
    hospital cadastrado (assume-se um unico hospital por instalacao) para
    obter o horario oficial de visitas.
    """

    DURACAO_SLOT_MINUTOS = 30          # tamanho de cada slot de visita
    JANELA_VISITA_HORAS = 4            # janela diaria de visitas (doc: "distribuicao em 4h")
    CAPACIDADE_MAXIMA_SIMULTANEA = 2   # numero maximo de visitantes por slot/leito

    @staticmethod
    def sp_verificar_disponibilidade_slots(id_leito, data_visita):
        """
        sp_verificar_disponibilidade_slots(id_leito, data_visita)

        Parametros de entrada:
            id_leito (int): id do leito consultado.
            data_visita (date): dia para o qual se quer os slots.

        Logica:
            1. Busca o leito e o horario oficial de inicio das visitas
               (hospital.horario_visita).
            2. Gera a lista de slots possiveis dentro da janela de visitas.
            3. Para cada slot, faz JOIN entre Internacao (para achar as
               internacoes daquele leito) e Visita, usando COUNT() para
               contar quantas reservas ativas ja existem naquele horario.
            4. Compara a contagem com CAPACIDADE_MAXIMA_SIMULTANEA.
            5. Filtra (WHERE) apenas os slots com vagas restantes > 0.
            6. Ordena por horario (ORDER BY horario ASC).

        Retorno:
            list[dict]: [{"horario": datetime, "vagas_restantes": int}, ...]
        """
        leito = Leito.query.get(id_leito)
        if leito is None:
            raise ValueError(f"Leito {id_leito} nao encontrado.")

        hospital = Hospital.query.first()
        if hospital is None:
            raise ValueError("Nenhum hospital cadastrado para obter o horario oficial de visitas.")

        hora_inicio = hospital.horario_visita.time()
        inicio_janela = datetime.combine(data_visita, hora_inicio)
        fim_janela = inicio_janela + timedelta(hours=LeitoRepository.JANELA_VISITA_HORAS)

        slots = []
        cursor = inicio_janela
        while cursor < fim_janela:
            slots.append(cursor)
            cursor += timedelta(minutes=LeitoRepository.DURACAO_SLOT_MINUTOS)

        disponiveis = []
        for horario_slot in slots:
            proximo_slot = horario_slot + timedelta(minutes=LeitoRepository.DURACAO_SLOT_MINUTOS)

            total_reservado = (
                db.session.query(func.count(Visita.id))
                .join(Internacao, Visita.id_internacao == Internacao.id)
                .filter(
                    Internacao.id_leito == id_leito,
                    Visita.status == True,  # noqa: E712 - visita ativa/confirmada
                    Visita.data_hora >= horario_slot,
                    Visita.data_hora < proximo_slot,
                )
                .scalar()
            ) or 0

            vagas_restantes = LeitoRepository.CAPACIDADE_MAXIMA_SIMULTANEA - total_reservado
            if vagas_restantes > 0:
                disponiveis.append({
                    "horario": horario_slot,
                    "vagas_restantes": vagas_restantes,
                })

        disponiveis.sort(key=lambda slot: slot["horario"])
        return disponiveis