from flask import request, jsonify
from models import Visitante
from services import VisitanteService
from .helpers import parse_datetime, campos_faltando, tratar_erros

class VisitanteController:
    @classmethod
    def listar(cls):
        visitantes = Visitante.listar_todos()
        return jsonify([v.to_dict() for v in visitantes]), 200

    @classmethod
    def buscar(cls, id):
        visitante = Visitante.buscar_por_id(id)
        if not visitante:
            return jsonify({"erro": "Visitante n�o encontrado"}), 404
        return jsonify(visitante.to_dict()), 200

    @classmethod
    @tratar_erros
    def cadastrar(cls):
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        obrigatorios = ['status', 'tipo', 'nome', 'data_nascimento', 'termo_consentimento', 'cpf']
        faltando = campos_faltando(dados, obrigatorios)
        if faltando:
            return jsonify({"erro": f"Campos obrigat�rios faltando: {', '.join(faltando)}"}), 400

        data_nascimento = parse_datetime(dados.get('data_nascimento'))
        if data_nascimento is None:
            return jsonify({"erro": "data_nascimento inv�lida. Use formato ISO 8601"}), 400

        if not dados.get('termo_consentimento'):
            return jsonify({"erro": "� necess�rio aceitar o termo de consentimento"}), 400

        if Visitante.query.filter_by(cpf=dados['cpf']).first():
            return jsonify({"erro": "J� existe um visitante com esse CPF"}), 400

        novo = Visitante(
            status=dados['status'],
            tipo=dados['tipo'],
            nome=dados['nome'],
            data_nascimento=data_nascimento,
            termo_consentimento=dados['termo_consentimento'],
            cpf=dados['cpf']
        )
        novo.salvar()
        return jsonify(novo.to_dict()), 201

    @classmethod
    @tratar_erros
    def atualizar(cls, id):
        visitante = Visitante.buscar_por_id(id)
        if not visitante:
            return jsonify({"erro": "Visitante n�o encontrado"}), 404

        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        data_nascimento = parse_datetime(dados.get('data_nascimento')) if 'data_nascimento' in dados else None
        if 'data_nascimento' in dados and data_nascimento is None:
            return jsonify({"erro": "data_nascimento inv�lida. Use formato ISO 8601"}), 400

        visitante.atualizar(
            status=dados.get('status'),
            tipo=dados.get('tipo'),
            nome=dados.get('nome'),
            data_nascimento=data_nascimento,
            termo_consentimento=dados.get('termo_consentimento'),
            cpf=dados.get('cpf')
        )
        return jsonify(visitante.to_dict()), 200

    @classmethod
    @tratar_erros
    def revogar(cls, id):
        visitante = Visitante.buscar_por_id(id)
        if not visitante:
            return jsonify({"erro": "Visitante não encontrado"}), 404
        visitante.revogar()
        return jsonify(visitante.to_dict()), 200

    @classmethod
    @tratar_erros
    def excluir(cls, id):
        visitante = Visitante.buscar_por_id(id)
        if not visitante:
            return jsonify({"erro": "Visitante n�o encontrado"}), 404
        visitante.deletar()
        return jsonify({"mensagem": "Visitante removido com sucesso"}), 200

    @classmethod
    @tratar_erros
    def regras_acesso(cls, id):
        """sp_obter_regras_acesso_por_papel: GET /visitantes/<id>/regras-acesso"""
        try:
            regras = VisitanteService.obter_regras_acesso(id)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 404
        return jsonify(regras), 200

    @classmethod
    @tratar_erros
    def cadastros_pendentes(cls):
        """sp_listar_cadastros_pendentes: GET /visitantes/pendentes"""
        pendentes = VisitanteService.listar_pendentes()
        return jsonify(pendentes), 200
