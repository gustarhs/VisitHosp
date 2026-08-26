from datetime import datetime

from extensions import db
from models.internacao import Internacao
from models.visita import Visita
from models.leito import Leito
from models.paciente import Paciente


class InternacaoRepository:
    """
    Camada de repository para o agregado Internacao.
    """

    @staticmethod
    def sp_cancelar_acessos_por_alta(id_leito):
        """
        sp_cancelar_acessos_por_alta(id_leito, evento_alta)

        Parametros de entrada: id_leito (o evento de alta em si e o disparo
        externo via integracao com o HIS; aqui assumimos que ele ja chegou
        e apenas executamos a invalidacao em lote).

        Logica:
            1. Localiza as internacoes ativas (status=True) daquele leito
               (WHERE id_leito = ? AND status = 'ativo').
            2. Localiza todas as visitas futuras/ativas vinculadas a essas
               internacoes.
            3. Executa UPDATE em massa, mudando o status desses registros
               (internacao = token de acesso, visita = QR Code) para
               invalidado/cancelado.

        Retorno: int - quantidade de registros invalidados (internacoes +
        visitas), para confirmacao/log.
        """
        internacoes = Internacao.query.filter_by(id_leito=id_leito, status=True).all()

        total_invalidados = 0
        agora = datetime.now()

        for internacao in internacoes:
            visitas = Visita.query.filter(
                Visita.id_internacao == internacao.id,
                Visita.status == True,  # noqa: E712
                Visita.data_hora >= agora,
            ).all()

            for visita in visitas:
                visita.status = False
                total_invalidados += 1

            internacao.status = False
            total_invalidados += 1

        db.session.commit()
        return total_invalidados

    @staticmethod
    def sp_validar_token_acesso(codigo_token):
        """
        sp_validar_token_acesso(codigo_token)

        Logica:
            1. Busca o token na tabela de internacoes
               (WHERE token_acesso = ? AND status = 'ativo').
            2. JOIN com leito e paciente para recuperar a internacao a que
               o token pertence.

        Retorno: dict com internacao/leito/paciente vinculados, ou None se
        o token for invalido/inexistente.
        """
        internacao = Internacao.query.filter_by(token_acesso=codigo_token, status=True).first()
        if internacao is None:
            return None

        leito = Leito.query.get(internacao.id_leito)
        paciente = Paciente.query.get(internacao.id_paciente)

        return {
            "internacao": internacao.to_dict(),
            "leito": leito.to_dict() if leito else None,
            "paciente": paciente.to_dict() if paciente else None,
        }