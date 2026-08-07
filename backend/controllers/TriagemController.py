from flask import Blueprint, request, jsonify
from models.triagem import Triagem
from .helpers import parse_datetime, campos_faltando, tratar_erros

triagem_bp = Blueprint('triagem_bp', __name__, url_prefix='/triagens')


@triagem_bp.route('', methods=['GET'])
def listar_triagens():
    triagens = Triagem.listar_todos()
    return jsonify([t.to_dict() for t in triagens]), 200


@triagem_bp.route('/<int:id>', methods=['GET'])
def buscar_triagem(id):
    triagem = Triagem.buscar_por_id(id)
    if not triagem:
        return jsonify({"erro": "Triagem não encontrada"}), 404
    return jsonify(triagem.to_dict()), 200


@triagem_bp.route('', methods=['POST'])
@tratar_erros
def criar_triagem():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    obrigatorios = ['data_hora', 'resultado', 'perguntas', 'respostas']
    faltando = campos_faltando(dados, obrigatorios)
    if faltando:
        return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(faltando)}"}), 400

    data_hora = parse_datetime(dados.get('data_hora'))
    if data_hora is None:
        return jsonify({"erro": "data_hora inválida. Use formato ISO 8601 (ex: 2026-08-06T14:00:00)"}), 400

    nova = Triagem(
        data_hora=data_hora,
        resultado=dados['resultado'],
        perguntas=dados['perguntas'],
        respostas=dados['respostas']
    )
    nova.salvar()
    return jsonify(nova.to_dict()), 201


@triagem_bp.route('/<int:id>', methods=['PUT'])
@tratar_erros
def atualizar_triagem(id):
    triagem = Triagem.buscar_por_id(id)
    if not triagem:
        return jsonify({"erro": "Triagem não encontrada"}), 404

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    data_hora = parse_datetime(dados.get('data_hora')) if 'data_hora' in dados else None
    if 'data_hora' in dados and data_hora is None:
        return jsonify({"erro": "data_hora inválida. Use formato ISO 8601"}), 400

    triagem.atualizar(
        data_hora=data_hora,
        resultado=dados.get('resultado'),
        perguntas=dados.get('perguntas'),
        respostas=dados.get('respostas')
    )
    return jsonify(triagem.to_dict()), 200


@triagem_bp.route('/<int:id>', methods=['DELETE'])
@tratar_erros
def deletar_triagem(id):
    triagem = Triagem.buscar_por_id(id)
    if not triagem:
        return jsonify({"erro": "Triagem não encontrada"}), 404
    triagem.deletar()
    return jsonify({"mensagem": "Triagem removida com sucesso"}), 200