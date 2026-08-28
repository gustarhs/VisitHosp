from flask import request, jsonify
from models import Leito
from services import LeitoService
from .helpers import campos_faltando, tratar_erros

class LeitoController:
    @classmethod
    def listar(cls):
        leitos = Leito.listar_todos()
        return jsonify([l.to_dict() for l in leitos]), 200

    @classmethod
    def buscar(cls, id):
        leito = Leito.buscar_por_id(id)
        if not leito:
            return jsonify({"erro": "Leito n�o encontrado"}), 404
        return jsonify(leito.to_dict()), 200

    @classmethod
    @tratar_erros
    def cadastrar(cls):
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        obrigatorios = ['status', 'ala', 'numero', 'andar', 'bloco']
        faltando = campos_faltando(dados, obrigatorios)
        if faltando:
            return jsonify({"erro": f"Campos obrigat�rios faltando: {', '.join(faltando)}"}), 400

        novo = Leito(
            status=dados['status'],
            ala=dados['ala'],
            numero=dados['numero'],
            andar=dados['andar'],
            bloco=dados['bloco']
        )
        novo.salvar()
        return jsonify(novo.to_dict()), 201

    @classmethod
    @tratar_erros
    def atualizar(cls, id):
        leito = Leito.buscar_por_id(id)
        if not leito:
            return jsonify({"erro": "Leito n�o encontrado"}), 404

        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        leito.atualizar(
            status=dados.get('status'),
            ala=dados.get('ala'),
            numero=dados.get('numero'),
            andar=dados.get('andar'),
            bloco=dados.get('bloco')
        )
        return jsonify(leito.to_dict()), 200

    @classmethod
    @tratar_erros
    def excluir(cls, id):
        leito = Leito.buscar_por_id(id)
        if not leito:
            return jsonify({"erro": "Leito n�o encontrado"}), 404
        leito.deletar()
        return jsonify({"mensagem": "Leito removido com sucesso"}), 200

    @classmethod
    @tratar_erros
    def disponibilidade_slots(cls, id):
        """sp_verificar_disponibilidade_slots: GET /leitos/<id>/disponibilidade?data_visita=YYYY-MM-DD"""
        data_visita = request.args.get('data_visita')
        if not data_visita:
            return jsonify({"erro": "Parâmetro 'data_visita' é obrigatório (YYYY-MM-DD)"}), 400

        try:
            slots = LeitoService.verificar_disponibilidade_slots(id, data_visita)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        slots_serializados = [
            {"horario": s["horario"].isoformat(), "vagas_restantes": s["vagas_restantes"]}
            for s in slots
        ]
        return jsonify(slots_serializados), 200
