from models.visitante import Visitante


class VisitanteRepository:
    """
    Camada de repository para o agregado Visitante.

    ATENCAO - limitacoes do schema atual (nenhuma alteracao de banco foi feita):
    - Nao existe uma tabela propria de "regras de acesso por papel". As
      regras abaixo (duracao maxima, areas permitidas, tipo de acesso) sao
      mantidas como configuracao no codigo, indexadas pelo valor de
      visitante.tipo ('acompanhante' ou 'visitante').
    - "Cadastro pendente" e representado pelo booleano visitante.status:
      False = aguardando aprovacao (pendente), True = aprovado/ativo. Nao
      existe campo data_envio na tabela, entao a ordenacao usa o id como
      proxy da ordem de cadastro.
    """

    REGRAS_POR_PAPEL = {
        "acompanhante": {
            "duracao_maxima_minutos": 480,
            "areas_permitidas": ["quarto", "refeitorio", "area_comum"],
            "tipo_acesso": "recorrente",
        },
        "visitante": {
            "duracao_maxima_minutos": 60,
            "areas_permitidas": ["quarto"],
            "tipo_acesso": "efemero",
        },
    }

    @staticmethod
    def sp_obter_regras_acesso_por_papel(id_visitante, id_paciente=None):
        """
        sp_obter_regras_acesso_por_papel(id_visitante, id_paciente)

        Parametros de entrada: id_visitante, id_paciente (mantido por
        compatibilidade com o requisito original; nao e usado na consulta,
        pois o papel ja esta no proprio cadastro do visitante).

        Logica:
            1. Busca visitante.tipo (papel: acompanhante/visitante).
            2. Consulta REGRAS_POR_PAPEL para o papel encontrado (equivalente
               ao JOIN com a tabela de regras de acesso por papel).

        Retorno: dict com duracao_maxima_minutos, areas_permitidas e
        tipo_acesso.
        """
        visitante = Visitante.query.get(id_visitante)
        if visitante is None:
            raise ValueError(f"Visitante {id_visitante} nao encontrado.")

        regra = VisitanteRepository.REGRAS_POR_PAPEL.get(visitante.tipo)
        if regra is None:
            raise ValueError(f"Nao ha regra de acesso configurada para o papel '{visitante.tipo}'.")

        return regra

    @staticmethod
    def sp_listar_cadastros_pendentes(id_hospital=None):
        """
        sp_listar_cadastros_pendentes(id_hospital, status)

        Parametros de entrada: id_hospital (opcional; nao aplicavel no
        schema atual, pois visitante nao possui vinculo direto com hospital).

        Logica:
            1. Filtra (WHERE status = 'pendente') os visitantes com
               status == False.
            2. Ordena por id (proxy de ordem de envio).

        Retorno: lista de cadastros pendentes com dados resumidos para
        analise do administrador.
        """
        pendentes = (
            Visitante.query
            .filter(Visitante.status == False)  # noqa: E712
            .order_by(Visitante.id.asc())
            .all()
        )
        return [v.to_dict() for v in pendentes]