from flask import Blueprint, request, jsonify
from models.hospital import Hospital
from .helpers import parse_datetime, campos_faltando, tratar_erros

hospital_bp = Blueprint('hospital_bp', __name__, url_prefix='/hospitais')


@hospital_bp.route('', methods=['GET'])
def listar_hospitais():
    hospitais = Hospital.listar_todos()
    return jsonify([h.to_dict() for h in hospitais]), 200


@hospital_bp.route('/<int:id>', methods=['GET'])
def buscar_hospital(id):
    hospital = Hospital.buscar_por_id(id)
    if not hospital:
        return jsonify({"erro": "Hospital não encontrado"}), 404
    return jsonify(hospital.to_dict()), 200


@hospital_bp.route('', methods=['POST'])
@tratar_erros
def criar_hospital():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    obrigatorios = ['nome', 'horario_visita', 'rua', 'numero', 'cidade', 'estado']
    faltando = campos_faltando(dados, obrigatorios)
    if faltando:
        return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(faltando)}"}), 400

    horario_visita = parse_datetime(dados.get('horario_visita'))
    if horario_visita is None:
        return jsonify({"erro": "horario_visita inválido. Use formato ISO 8601 (ex: 2026-08-06T14:00:00)"}), 400

    novo = Hospital(
        nome=dados['nome'],
        horario_visita=horario_visita,
        rua=dados['rua'],
        numero=dados['numero'],
        cidade=dados['cidade'],
        estado=dados['estado']
    )
    novo.salvar()
    return jsonify(novo.to_dict()), 201


@hospital_bp.route('/<int:id>', methods=['PUT'])
@tratar_erros
def atualizar_hospital(id):
    hospital = Hospital.buscar_por_id(id)
    if not hospital:
        return jsonify({"erro": "Hospital não encontrado"}), 404

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição vazio ou inválido"}), 400

    horario_visita = parse_datetime(dados.get('horario_visita')) if 'horario_visita' in dados else None
    if 'horario_visita' in dados and horario_visita is None:
        return jsonify({"erro": "horario_visita inválido. Use formato ISO 8601"}), 400

    hospital.atualizar(
        nome=dados.get('nome'),
        horario_visita=horario_visita,
        rua=dados.get('rua'),
        numero=dados.get('numero'),
        cidade=dados.get('cidade'),
        estado=dados.get('estado')
    )
    return jsonify(hospital.to_dict()), 200


@hospital_bp.route('/<int:id>', methods=['DELETE'])
@tratar_erros
def deletar_hospital(id):
    hospital = Hospital.buscar_por_id(id)
    if not hospital:
        return jsonify({"erro": "Hospital não encontrado"}), 404
    hospital.deletar()
    return jsonify({"mensagem": "Hospital removido com sucesso"}), 200