from flask import request, jsonify

from services.consulta.consulta_service import ConsultaService
from ._servico_base import responder


class ConsultaController:

    @classmethod
    @responder
    def regulamento(cls):
        """Req. 1 - GET /regulamento"""
        return jsonify(ConsultaService.obter_regulamento()), 200

    @classmethod
    @responder
    def status_paciente(cls, id):
        """Req. 2 - GET /pacientes/<id>/status"""
        return jsonify(ConsultaService.status_paciente(id)), 200

    @classmethod
    @responder
    def localizacao_leito(cls, id):
        """Req. 3 - GET /leitos/<id>/localizacao"""
        return jsonify(ConsultaService.localizacao_leito(id)), 200

    @classmethod
    @responder
    def horarios_ocupados_leito(cls, id):
        """Req. 6 - GET /leitos/<id>/horarios-ocupados?data=YYYY-MM-DD"""
        return jsonify(ConsultaService.horarios_ocupados_leito(id, request.args.get("data"))), 200
