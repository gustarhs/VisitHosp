from flask import Blueprint, request, jsonify
from models.internacao import Internacao
from models.paciente import Paciente
from models.leito import Leito
from .helpers import parse_datetime, campos_faltando, tratar_erros

internacao_bp = Blueprint('internacao_bp', __name__, url_prefix='/internacoes')


@internacao_bp.route('', methods=['GET'])
def listar_internacoes():
    internacoes = Internacao.listar_todos()
    return jsonify([i.to_dict() for i in internacoes]), 200


@internacao_bp.route('/<int:id>', methods=['GET'])
def buscar_internacao(id):
    internacao = Internacao.buscar_por_id(id)
    if not internacao:
        return jsonify({"erro": "Internação não encontrada"}), 404
    return jsonify(internacao.to_dict()), 200


@internacao_bp.route('', methods=['POST'])
@tratar_erros
def criar_internacao():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    obrigatorios = ['data_entrada', 'data_saida', 'status', 'token_acesso', 'id_paciente', 'id_leito']
    faltando = campos_faltando(dados, obrigatorios)
    if faltando:
        return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(faltando)}"}), 400

    data_entrada = parse_datetime(dados.get('data_entrada'))
    data_saida = parse_datetime(dados.get('data_saida'))
    if data_entrada is None or data_saida is None:
        return jsonify({"erro": "data_entrada/data_saida inválidas. Use formato ISO 8601"}), 400

    if not Paciente.buscar_por_id(dados['id_paciente']):
        return jsonify({"erro": "Paciente não encontrado"}), 404
    if not Leito.buscar_por_id(dados['id_leito']):
        return jsonify({"erro": "Leito não encontrado"}), 404

    nova = Internacao(
        data_entrada=data_entrada,
        data_saida=data_saida,
        status=dados['status'],
        token_acesso=dados['token_acesso'],
        id_paciente=dados['id_paciente'],
        id_leito=dados['id_leito']
    )
    nova.salvar()
    return jsonify(nova.to_dict()), 201


@internacao_bp.route('/<int:id>', methods=['PUT'])
@tratar_erros
def atualizar_internacao(id):
    internacao = Internacao.buscar_por_id(id)
    if not internacao:
        return jsonify({"erro": "Internação não encontrada"}), 404

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    if 'id_paciente' in dados and not Paciente.buscar_por_id(dados['id_paciente']):
        return jsonify({"erro": "Paciente não encontrado"}), 404
    if 'id_leito' in dados and not Leito.buscar_por_id(dados['id_leito']):
        return jsonify({"erro": "Leito não encontrado"}), 404

    data_entrada = parse_datetime(dados.get('data_entrada')) if 'data_entrada' in dados else None
    data_saida = parse_datetime(dados.get('data_saida')) if 'data_saida' in dados else None
    if 'data_entrada' in dados and data_entrada is None:
        return jsonify({"erro": "data_entrada inválida. Use formato ISO 8601"}), 400
    if 'data_saida' in dados and data_saida is None:
        return jsonify({"erro": "data_saida inválida. Use formato ISO 8601"}), 400

    # NOTA: o método atualizar() do model precisa aceitar id_paciente e id_leito
    # como parâmetros (veja aviso no chat sobre as FKs faltando no model).
    internacao.atualizar(
        data_entrada=data_entrada,
        data_saida=data_saida,
        status=dados.get('status'),
        token_acesso=dados.get('token_acesso'),
        id_paciente=dados.get('id_paciente'),
        id_leito=dados.get('id_leito')
    )
    return jsonify(internacao.to_dict()), 200


@internacao_bp.route('/<int:id>', methods=['DELETE'])
@tratar_erros
def deletar_internacao(id):
    internacao = Internacao.buscar_por_id(id)
    if not internacao:
        return jsonify({"erro": "Internação não encontrada"}), 404
    internacao.deletar()
    return jsonify({"mensagem": "Internação removida com sucesso"}), 200