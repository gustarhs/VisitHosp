from flask import request, jsonify

from services.vinculo.vinculo_service import VinculoService
from services.comum import Invalido
from ._servico_base import responder


class VinculoController:

    @classmethod
    @responder
    def cadastrar(cls):
        """Req. 7 - POST /visitantes/cadastro-vinculado"""
        dados = request.get_json(silent=True)
        if not dados:
            raise Invalido("Corpo da requisição vazio ou inválido.")
        return jsonify(VinculoService.cadastrar_visitante_vinculado(dados)), 201

    @classmethod
    @responder
    def listar_por_paciente(cls, id):
        """GET /pacientes/<id>/visitantes"""
        return jsonify(VinculoService.listar_vinculos_paciente(id)), 200

    @classmethod
    @responder
    def revogar(cls, id):
        """Req. 4 - POST /visitantes/<id>/revogar-acesso  body: {"id_paciente": 1, "motivo": "..."}"""
        dados = request.get_json(silent=True) or {}
        return jsonify(VinculoService.revogar_acesso(id, dados.get("id_paciente"), dados.get("motivo"))), 200
