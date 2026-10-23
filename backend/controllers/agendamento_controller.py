from flask import request, jsonify

from services.agendamento.agendamento_service import AgendamentoService
from services.comum import Invalido
from ._servico_base import responder


class AgendamentoController:

    @classmethod
    @responder
    def listar_por_internacao(cls, id):
        """GET /internacoes/<id>/visitas?id_visitante=..."""
        return jsonify(AgendamentoService.listar_por_internacao(id, request.args.get("id_visitante", type=int))), 200

    @classmethod
    @responder
    def cancelar(cls, id):
        """Req. 5 - POST /visitas/<id>/cancelar"""
        return jsonify(AgendamentoService.cancelar(id)), 200

    @classmethod
    @responder
    def reagendar(cls, id):
        """Req. 5 - POST /visitas/<id>/reagendar  body: {"data_hora": "2026-10-23T14:00:00"}"""
        dados = request.get_json(silent=True) or {}
        if not dados.get("data_hora"):
            raise Invalido("Campo 'data_hora' é obrigatório.")
        return jsonify(AgendamentoService.reagendar(id, dados["data_hora"])), 200
