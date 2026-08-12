from flask import request, jsonify
from models import Triagem
from .helpers import parse_datetime, campos_faltando, tratar_erros

class TriagemController:
    @classmethod
    def listar(cls):
        triagens = Triagem.listar_todos()
        return jsonify([t.to_dict() for t in triagens]), 200

    @classmethod
    def buscar(cls, id):
        triagem = Triagem.buscar_por_id(id)
        if not triagem:
            return jsonify({"erro": "Triagem n�o encontrada"}), 404
        return jsonify(triagem.to_dict()), 200

    @classmethod
    @tratar_erros
    def cadastrar(cls):
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        obrigatorios = ['data_hora', 'resultado', 'perguntas', 'respostas']
        faltando = campos_faltando(dados, obrigatorios)
        if faltando:
            return jsonify({"erro": f"Campos obrigat�rios faltando: {', '.join(faltando)}"}), 400

        data_hora = parse_datetime(dados.get('data_hora'))
        if data_hora is None:
            return jsonify({"erro": "data_hora inv�lida. Use formato ISO 8601 (ex: 2026-08-06T14:00:00)"}), 400

        nova = Triagem(
            data_hora=data_hora,
            resultado=dados['resultado'],
            perguntas=dados['perguntas'],
            respostas=dados['respostas']
        )
        nova.salvar()
        return jsonify(nova.to_dict()), 201

    @classmethod
    @tratar_erros
    def atualizar(cls, id):
        triagem = Triagem.buscar_por_id(id)
        if not triagem:
            return jsonify({"erro": "Triagem n�o encontrada"}), 404

        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        data_hora = parse_datetime(dados.get('data_hora')) if 'data_hora' in dados else None
        if 'data_hora' in dados and data_hora is None:
            return jsonify({"erro": "data_hora inv�lida. Use formato ISO 8601"}), 400

        triagem.atualizar(
            data_hora=data_hora,
            resultado=dados.get('resultado'),
            perguntas=dados.get('perguntas'),
            respostas=dados.get('respostas')
        )
        return jsonify(triagem.to_dict()), 200

    @classmethod
    @tratar_erros
    def excluir(cls, id):
        triagem = Triagem.buscar_por_id(id)
        if not triagem:
            return jsonify({"erro": "Triagem n�o encontrada"}), 404
        triagem.deletar()
        return jsonify({"mensagem": "Triagem removida com sucesso"}), 200
