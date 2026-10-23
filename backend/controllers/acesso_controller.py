from flask import request, jsonify

from services.acesso.acesso_service import AcessoService
from ._servico_base import responder


class AcessoController:

    @classmethod
    @responder
    def checkin(cls, id):
        """POST /visitas/<id>/checkin"""
        return jsonify(AcessoService.registrar_checkin(id)), 201

    @classmethod
    @responder
    def checkout(cls, id):
        """POST /visitas/<id>/checkout"""
        return jsonify(AcessoService.registrar_checkout(id)), 201

    @classmethod
    @responder
    def historico_visitas(cls):
        """Req. 8 - GET /relatorios/historico-visitas?id_paciente=&data_inicio=&data_fim="""
        return jsonify(AcessoService.historico_visitas(
            request.args.get("id_paciente", type=int),
            request.args.get("data_inicio"),
            request.args.get("data_fim"),
        )), 200

    @classmethod
    @responder
    def auditoria_acessos(cls):
        """Req. 9 - GET /relatorios/auditoria-acessos?periodo_inicio=&periodo_fim=&id_leito=&id_paciente="""
        return jsonify(AcessoService.auditoria_acessos(
            request.args.get("periodo_inicio"),
            request.args.get("periodo_fim"),
            request.args.get("id_leito", type=int),
            request.args.get("id_paciente", type=int),
        )), 200

    @classmethod
    @responder
    def visitantes_por_turno(cls):
        """Req. 10 - GET /relatorios/visitantes-por-turno?periodo_inicio=&periodo_fim="""
        return jsonify(AcessoService.visitantes_por_turno(
            request.args.get("periodo_inicio"),
            request.args.get("periodo_fim"),
        )), 200
