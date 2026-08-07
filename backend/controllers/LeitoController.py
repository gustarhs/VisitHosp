from flask import Blueprint, request, jsonify
from models.leito import Leito
from .helpers import campos_faltando, tratar_erros

leito_bp = Blueprint('leito_bp', __name__, url_prefix='/leitos')


@leito_bp.route('', methods=['GET'])
def listar_leitos():
    leitos = Leito.listar_todos()
    return jsonify([l.to_dict() for l in leitos]), 200


@leito_bp.route('/<int:id>', methods=['GET'])
def buscar_leito(id):
    leito = Leito.buscar_por_id(id)
    if not leito:
        return jsonify({"erro": "Leito não encontrado"}), 404
    return jsonify(leito.to_dict()), 200


@leito_bp.route('', methods=['POST'])
@tratar_erros
def criar_leito():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    obrigatorios = ['status', 'ala', 'numero', 'andar', 'bloco']
    faltando = campos_faltando(dados, obrigatorios)
    if faltando:
        return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(faltando)}"}), 400

    novo = Leito(
        status=dados['status'],
        ala=dados['ala'],
        numero=dados['numero'],
        andar=dados['andar'],
        bloco=dados['bloco']
    )
    novo.salvar()
    return jsonify(novo.to_dict()), 201


@leito_bp.route('/<int:id>', methods=['PUT'])
@tratar_erros
def atualizar_leito(id):
    leito = Leito.buscar_por_id(id)
    if not leito:
        return jsonify({"erro": "Leito não encontrado"}), 404

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    leito.atualizar(
        status=dados.get('status'),
        ala=dados.get('ala'),
        numero=dados.get('numero'),
        andar=dados.get('andar'),
        bloco=dados.get('bloco')
    )
    return jsonify(leito.to_dict()), 200


@leito_bp.route('/<int:id>', methods=['DELETE'])
@tratar_erros
def deletar_leito(id):
    leito = Leito.buscar_por_id(id)
    if not leito:
        return jsonify({"erro": "Leito não encontrado"}), 404
    leito.deletar()
    return jsonify({"mensagem": "Leito removido com sucesso"}), 200