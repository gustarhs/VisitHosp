from flask import request, jsonify
from models import Internacao, Paciente, Leito
from services import InternacaoService
from .helpers import parse_datetime, campos_faltando, tratar_erros

class InternacaoController:
    @classmethod
    def listar(cls):
        internacoes = Internacao.listar_todos()
        return jsonify([i.to_dict() for i in internacoes]), 200

    @classmethod
    def buscar(cls, id):
        internacao = Internacao.buscar_por_id(id)
        if not internacao:
            return jsonify({"erro": "Interna��o n�o encontrada"}), 404
        return jsonify(internacao.to_dict()), 200

    @classmethod
    @tratar_erros
    def cadastrar(cls):
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        obrigatorios = ['data_entrada', 'data_saida', 'status', 'token_acesso', 'id_paciente', 'id_leito']
        faltando = campos_faltando(dados, obrigatorios)
        if faltando:
            return jsonify({"erro": f"Campos obrigat�rios faltando: {', '.join(faltando)}"}), 400

        data_entrada = parse_datetime(dados.get('data_entrada'))
        data_saida = parse_datetime(dados.get('data_saida'))
        if data_entrada is None or data_saida is None:
            return jsonify({"erro": "data_entrada/data_saida inv�lidas. Use formato ISO 8601"}), 400

        if not Paciente.buscar_por_id(dados['id_paciente']):
            return jsonify({"erro": "Paciente n�o encontrado"}), 404
        if not Leito.buscar_por_id(dados['id_leito']):
            return jsonify({"erro": "Leito n�o encontrado"}), 404

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

    @classmethod
    @tratar_erros
    def atualizar(cls, id):
        internacao = Internacao.buscar_por_id(id)
        if not internacao:
            return jsonify({"erro": "Interna��o n�o encontrada"}), 404

        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        if 'id_paciente' in dados and not Paciente.buscar_por_id(dados['id_paciente']):
            return jsonify({"erro": "Paciente n�o encontrado"}), 404
        if 'id_leito' in dados and not Leito.buscar_por_id(dados['id_leito']):
            return jsonify({"erro": "Leito n�o encontrado"}), 404

        data_entrada = parse_datetime(dados.get('data_entrada')) if 'data_entrada' in dados else None
        data_saida = parse_datetime(dados.get('data_saida')) if 'data_saida' in dados else None
        if 'data_entrada' in dados and data_entrada is None:
            return jsonify({"erro": "data_entrada inv�lida. Use formato ISO 8601"}), 400
        if 'data_saida' in dados and data_saida is None:
            return jsonify({"erro": "data_saida inv�lida. Use formato ISO 8601"}), 400

        internacao.atualizar(
            data_entrada=data_entrada,
            data_saida=data_saida,
            status=dados.get('status'),
            token_acesso=dados.get('token_acesso'),
            id_paciente=dados.get('id_paciente'),
            id_leito=dados.get('id_leito')
        )
        return jsonify(internacao.to_dict()), 200

    @classmethod
    @tratar_erros
    def excluir(cls, id):
        internacao = Internacao.buscar_por_id(id)
        if not internacao:
            return jsonify({"erro": "Interna��o n�o encontrada"}), 404
        internacao.deletar()
        return jsonify({"mensagem": "Interna��o removida com sucesso"}), 200


    @classmethod
    @tratar_erros
    def dar_alta(cls, id_leito):
        """sp_cancelar_acessos_por_alta: POST /leitos/<id_leito>/dar-alta"""
        total_invalidados = InternacaoService.cancelar_por_alta(id_leito)
        return jsonify({"registros_invalidados": total_invalidados}), 200

    @classmethod
    @tratar_erros
    def validar_token(cls):
        """sp_validar_token_acesso: POST /internacoes/validar-token  body: {"codigo_token": "..."}"""
        dados = request.get_json(silent=True)
        if not dados or not dados.get('codigo_token'):
            return jsonify({"erro": "Campo \'codigo_token\' e obrigatorio"}), 400

        resultado = InternacaoService.validar_token(dados['codigo_token'])
        if resultado is None:
            return jsonify({"erro": "Token invalido, expirado ou inexistente"}), 404

        return jsonify(resultado), 200
