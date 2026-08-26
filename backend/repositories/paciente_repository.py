from models.paciente import Paciente
from models.internacao import Internacao
from models.visita import Visita
from models.visitante import Visitante


class PacienteRepository:
    """
    Camada de repository para o agregado Paciente.

    ATENCAO - limitacoes do schema atual (nenhuma alteracao de banco foi feita):
    - Nao existe um campo especifico para "status clinico" (critico,
      isolamento, procedimento, estavel). O booleano paciente.status e
      reaproveitado como flag de bloqueio: True = paciente em situacao que
      bloqueia visitas (critico/isolamento/procedimento), False = liberado.
    - Nao existe uma tabela de "responsaveis legais" (ADM1/ADM2). Essa
      informacao e inferida a partir dos visitantes que ja visitaram o
      paciente, usando a convencao visitante.tipo == 'ADM1' / 'ADM2'. E um
      contorno; o ideal seria uma tabela propria de vinculo
      paciente-responsavel com prioridade, mas isso exigiria alterar o
      banco, o que foi explicitamente evitado aqui.
    """

    @staticmethod
    def sp_verificar_bloqueio_status_paciente(id_paciente):
        """
        sp_verificar_bloqueio_status_paciente(id_paciente)

        Parametros de entrada: id_paciente (ou id_leito, ver observacao).

        Logica:
            1. Busca paciente.status (usado aqui como flag de status critico).
            2. Se o status critico estiver ativo, retorna flag de bloqueio.

        Retorno: {"bloqueado": bool, "motivo": str|None}
        """
        paciente = Paciente.query.get(id_paciente)
        if paciente is None:
            raise ValueError(f"Paciente {id_paciente} nao encontrado.")

        bloqueado = paciente.status is True
        return {
            "bloqueado": bloqueado,
            "motivo": "Paciente em situacao critica/isolamento/procedimento." if bloqueado else None,
        }

    @staticmethod
    def sp_obter_responsavel_autorizado(id_paciente):
        """
        sp_obter_responsavel_autorizado(id_paciente)

        Logica:
            1. Localiza visitantes que ja constam em visitas ligadas a
               internacoes desse paciente (JOIN visita -> internacao).
            2. Procura primeiro um visitante com tipo == 'ADM1' e status ativo.
            3. Se nao encontrar, faz fallback sequencial para tipo == 'ADM2'.

        Retorno: dict com nivel (ADM1/ADM2) e dados do responsavel, ou None
        se nenhum responsavel ativo for encontrado.
        """
        base_query = (
            Visitante.query
            .join(Visita, Visita.id_visitante == Visitante.id)
            .join(Internacao, Visita.id_internacao == Internacao.id)
            .filter(Internacao.id_paciente == id_paciente)
        )

        adm1 = base_query.filter(Visitante.tipo == "ADM1", Visitante.status == True).first()  # noqa: E712
        if adm1:
            return {"nivel": "ADM1", "responsavel": adm1.to_dict()}

        adm2 = base_query.filter(Visitante.tipo == "ADM2", Visitante.status == True).first()  # noqa: E712
        if adm2:
            return {"nivel": "ADM2", "responsavel": adm2.to_dict()}

        return None