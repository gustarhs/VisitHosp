from flask import Blueprint, request, jsonify
from models.paciente import Paciente
from .helpers import parse_datetime, campos_faltando, tratar_erros

paciente_bp = Blueprint('paciente_bp', __name__, url_prefix='/pacientes')


@paciente_bp.route('', methods=['GET'])
def listar_pacientes():
    pacientes = Paciente.listar_todos()
    return jsonify([p.to_dict() for p in pacientes]), 200


@paciente_bp.route('/<int:id>', methods=['GET'])
def buscar_paciente(id):
    paciente = Paciente.buscar_por_id(id)
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404
    return jsonify(paciente.to_dict()), 200


@paciente_bp.route('', methods=['POST'])
@tratar_erros
def criar_paciente():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    obrigatorios = ['data_nascimento', 'tipo', 'status', 'nome', 'cpf']
    faltando = campos_faltando(dados, obrigatorios)
    if faltando:
        return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(faltando)}"}), 400

    data_nascimento = parse_datetime(dados.get('data_nascimento'))
    if data_nascimento is None:
        return jsonify({"erro": "data_nascimento inválida. Use formato ISO 8601 (ex: 1990-05-20T00:00:00)"}), 400

    if Paciente.query.filter_by(cpf=dados['cpf']).first():
        return jsonify({"erro": "Já existe um paciente com esse CPF"}), 400

    novo = Paciente(
        data_nascimento=data_nascimento,
        tipo=dados['tipo'],
        status=dados['status'],
        nome=dados['nome'],
        cpf=dados['cpf']
    )
    novo.salvar()
    return jsonify(novo.to_dict()), 201


@paciente_bp.route('/<int:id>', methods=['PUT'])
@tratar_erros
def atualizar_paciente(id):
    paciente = Paciente.buscar_por_id(id)
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    data_nascimento = parse_datetime(dados.get('data_nascimento')) if 'data_nascimento' in dados else None
    if 'data_nascimento' in dados and data_nascimento is None:
        return jsonify({"erro": "data_nascimento inválida. Use formato ISO 8601"}), 400

    paciente.atualizar(
        data_nascimento=data_nascimento,
        tipo=dados.get('tipo'),
        status=dados.get('status'),
        nome=dados.get('nome'),
        cpf=dados.get('cpf')
    )
    return jsonify(paciente.to_dict()), 200


@paciente_bp.route('/<int:id>', methods=['DELETE'])
@tratar_erros
def deletar_paciente(id):
    paciente = Paciente.buscar_por_id(id)
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404
    paciente.deletar()
    return jsonify({"mensagem": "Paciente removido com sucesso"}), 200