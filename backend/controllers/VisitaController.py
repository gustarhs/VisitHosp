from flask import Blueprint, request, jsonify
from models.visita import Visita
from models.visitante import Visitante
from models.hospital import Hospital
from models.internacao import Internacao
from models.triagem import Triagem
from .helpers import parse_datetime, campos_faltando, tratar_erros

visita_bp = Blueprint('visita_bp', __name__, url_prefix='/visitas')


@visita_bp.route('', methods=['GET'])
def listar_visitas():
    visitas = Visita.listar_todos()
    return jsonify([v.to_dict() for v in visitas]), 200


@visita_bp.route('/<int:id>', methods=['GET'])
def buscar_visita(id):
    visita = Visita.buscar_por_id(id)
    if not visita:
        return jsonify({"erro": "Visita não encontrada"}), 404
    return jsonify(visita.to_dict()), 200


@visita_bp.route('', methods=['POST'])
@tratar_erros
def criar_visita():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    # id_triagem é opcional (nem toda visita precisa ter triagem já feita)
    obrigatorios = ['data_hora', 'status', 'qr_code', 'id_visitante', 'id_hospital', 'id_internacao']
    faltando = campos_faltando(dados, obrigatorios)
    if faltando:
        return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(faltando)}"}), 400

    data_hora = parse_datetime(dados.get('data_hora'))
    if data_hora is None:
        return jsonify({"erro": "data_hora inválida. Use formato ISO 8601"}), 400

    if not Visitante.buscar_por_id(dados['id_visitante']):
        return jsonify({"erro": "Visitante não encontrado"}), 404
    if not Hospital.buscar_por_id(dados['id_hospital']):
        return jsonify({"erro": "Hospital não encontrado"}), 404
    if not Internacao.buscar_por_id(dados['id_internacao']):
        return jsonify({"erro": "Internação não encontrada"}), 404
    if dados.get('id_triagem') is not None and not Triagem.buscar_por_id(dados['id_triagem']):
        return jsonify({"erro": "Triagem não encontrada"}), 404

    if Visita.query.filter_by(qr_code=dados['qr_code']).first():
        return jsonify({"erro": "Já existe uma visita com esse qr_code"}), 400

    nova = Visita(
        data_hora=data_hora,
        status=dados['status'],
        qr_code=dados['qr_code'],
        id_visitante=dados['id_visitante'],
        id_hospital=dados['id_hospital'],
        id_internacao=dados['id_internacao'],
        id_triagem=dados.get('id_triagem')
    )
    nova.salvar()
    return jsonify(nova.to_dict()), 201


@visita_bp.route('/<int:id>', methods=['PUT'])
@tratar_erros
def atualizar_visita(id):
    visita = Visita.buscar_por_id(id)
    if not visita:
        return jsonify({"erro": "Visita não encontrada"}), 404

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    if 'id_visitante' in dados and not Visitante.buscar_por_id(dados['id_visitante']):
        return jsonify({"erro": "Visitante não encontrado"}), 404
    if 'id_hospital' in dados and not Hospital.buscar_por_id(dados['id_hospital']):
        return jsonify({"erro": "Hospital não encontrado"}), 404
    if 'id_internacao' in dados and not Internacao.buscar_por_id(dados['id_internacao']):
        return jsonify({"erro": "Internação não encontrada"}), 404
    if 'id_triagem' in dados and dados['id_triagem'] is not None and not Triagem.buscar_por_id(dados['id_triagem']):
        return jsonify({"erro": "Triagem não encontrada"}), 404

    data_hora = parse_datetime(dados.get('data_hora')) if 'data_hora' in dados else None
    if 'data_hora' in dados and data_hora is None:
        return jsonify({"erro": "data_hora inválida. Use formato ISO 8601"}), 400

    # NOTA: o método atualizar() do model precisa aceitar id_visitante, id_hospital,
    # id_internacao e id_triagem como parâmetros (veja aviso sobre as FKs faltando).
    visita.atualizar(
        data_hora=data_hora,
        status=dados.get('status'),
        qr_code=dados.get('qr_code'),
        id_visitante=dados.get('id_visitante'),
        id_hospital=dados.get('id_hospital'),
        id_internacao=dados.get('id_internacao'),
        id_triagem=dados.get('id_triagem')
    )
    return jsonify(visita.to_dict()), 200


@visita_bp.route('/<int:id>', methods=['DELETE'])
@tratar_erros
def deletar_visita(id):
    visita = Visita.buscar_por_id(id)
    if not visita:
        return jsonify({"erro": "Visita não encontrada"}), 404
    visita.deletar()
    return jsonify({"mensagem": "Visita removida com sucesso"}), 200