from flask import request, jsonify
from models import Paciente
from .helpers import parse_datetime, campos_faltando, tratar_erros

class PacienteController:
    @classmethod
    def listar(cls):
        pacientes = Paciente.listar_todos()
        return jsonify([p.to_dict() for p in pacientes]), 200

    @classmethod
    def buscar(cls, id):
        paciente = Paciente.buscar_por_id(id)
        if not paciente:
            return jsonify({"erro": "Paciente n�o encontrado"}), 404
        return jsonify(paciente.to_dict()), 200

    @classmethod
    @tratar_erros
    def cadastrar(cls):
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        obrigatorios = ['data_nascimento', 'tipo', 'status', 'nome', 'cpf']
        faltando = campos_faltando(dados, obrigatorios)
        if faltando:
            return jsonify({"erro": f"Campos obrigat�rios faltando: {', '.join(faltando)}"}), 400

        data_nascimento = parse_datetime(dados.get('data_nascimento'))
        if data_nascimento is None:
            return jsonify({"erro": "data_nascimento inv�lida. Use formato ISO 8601 (ex: 1990-05-20T00:00:00)"}), 400

        if Paciente.query.filter_by(cpf=dados['cpf']).first():
            return jsonify({"erro": "J� existe um paciente com esse CPF"}), 400

        novo = Paciente(
            data_nascimento=data_nascimento,
            tipo=dados['tipo'],
            status=dados['status'],
            nome=dados['nome'],
            cpf=dados['cpf']
        )
        novo.salvar()
        return jsonify(novo.to_dict()), 201

    @classmethod
    @tratar_erros
    def atualizar(cls, id):
        paciente = Paciente.buscar_por_id(id)
        if not paciente:
            return jsonify({"erro": "Paciente n�o encontrado"}), 404

        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        data_nascimento = parse_datetime(dados.get('data_nascimento')) if 'data_nascimento' in dados else None
        if 'data_nascimento' in dados and data_nascimento is None:
            return jsonify({"erro": "data_nascimento inv�lida. Use formato ISO 8601"}), 400

        paciente.atualizar(
            data_nascimento=data_nascimento,
            tipo=dados.get('tipo'),
            status=dados.get('status'),
            nome=dados.get('nome'),
            cpf=dados.get('cpf')
        )
        return jsonify(paciente.to_dict()), 200

    @classmethod
    @tratar_erros
    def excluir(cls, id):
        paciente = Paciente.buscar_por_id(id)
        if not paciente:
            return jsonify({"erro": "Paciente n�o encontrado"}), 404
        paciente.deletar()
        return jsonify({"mensagem": "Paciente removido com sucesso"}), 200
