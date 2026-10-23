from flask import request, jsonify
from models import Visita, Visitante, Hospital, Internacao, Triagem
from services import VisitaService
from .helpers import parse_datetime, campos_faltando, tratar_erros

class VisitaController:
    @classmethod
    def listar(cls):
        visitas = Visita.listar_todos()
        return jsonify([v.to_dict() for v in visitas]), 200

    @classmethod
    def buscar(cls, id):
        visita = Visita.buscar_por_id(id)
        if not visita:
            return jsonify({"erro": "Visita n�o encontrada"}), 404
        return jsonify(visita.to_dict()), 200

    @classmethod
    @tratar_erros
    def cadastrar(cls):
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        obrigatorios = ['data_hora', 'status', 'qr_code', 'id_visitante', 'id_hospital', 'id_internacao']
        faltando = campos_faltando(dados, obrigatorios)
        if faltando:
            return jsonify({"erro": f"Campos obrigat�rios faltando: {', '.join(faltando)}"}), 400

        data_hora = parse_datetime(dados.get('data_hora'))
        if data_hora is None:
            return jsonify({"erro": "data_hora inv�lida. Use formato ISO 8601"}), 400

        visitante = Visitante.buscar_por_id(dados['id_visitante'])
        if not visitante:
            return jsonify({"erro": "Visitante n�o encontrado"}), 404
        if not visitante.ativo:
            return jsonify({"erro": "Acesso do visitante revogado"}), 403
        if not Hospital.buscar_por_id(dados['id_hospital']):
            return jsonify({"erro": "Hospital n�o encontrado"}), 404
        if not Internacao.buscar_por_id(dados['id_internacao']):
            return jsonify({"erro": "Interna��o n�o encontrada"}), 404
        if dados.get('id_triagem') is not None and not Triagem.buscar_por_id(dados['id_triagem']):
            return jsonify({"erro": "Triagem n�o encontrada"}), 404

        if Visita.query.filter_by(qr_code=dados['qr_code']).first():
            return jsonify({"erro": "J� existe uma visita com esse qr_code"}), 400

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

    @classmethod
    @tratar_erros
    def atualizar(cls, id):
        visita = Visita.buscar_por_id(id)
        if not visita:
            return jsonify({"erro": "Visita n�o encontrada"}), 404

        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisi��o vazio ou inv�lido"}), 400

        if 'id_visitante' in dados and not Visitante.buscar_por_id(dados['id_visitante']):
            return jsonify({"erro": "Visitante n�o encontrado"}), 404
        if 'id_hospital' in dados and not Hospital.buscar_por_id(dados['id_hospital']):
            return jsonify({"erro": "Hospital n�o encontrado"}), 404
        if 'id_internacao' in dados and not Internacao.buscar_por_id(dados['id_internacao']):
            return jsonify({"erro": "Interna��o n�o encontrada"}), 404
        if 'id_triagem' in dados and dados['id_triagem'] is not None and not Triagem.buscar_por_id(dados['id_triagem']):
            return jsonify({"erro": "Triagem n�o encontrada"}), 404

        data_hora = parse_datetime(dados.get('data_hora')) if 'data_hora' in dados else None
        if 'data_hora' in dados and data_hora is None:
            return jsonify({"erro": "data_hora inv�lida. Use formato ISO 8601"}), 400

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

    @classmethod
    @tratar_erros
    def excluir(cls, id):
        visita = Visita.buscar_por_id(id)
        if not visita:
            return jsonify({"erro": "Visita n�o encontrada"}), 404
        visita.deletar()
        return jsonify({"mensagem": "Visita removida com sucesso"}), 200

    @classmethod
    @tratar_erros
    def historico_paciente(cls, id):
        """sp_historico_visitas_paciente: GET /pacientes/<id>/visitas?data_inicio=...&data_fim=..."""
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')

        try:
            historico = VisitaService.historico_por_paciente(id, data_inicio, data_fim)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        return jsonify(historico), 200

    @classmethod
    @tratar_erros
    def relatorio_auditoria_fluxo(cls):
        """sp_relatorio_auditoria_fluxo: GET /relatorios/auditoria-fluxo?periodo_inicio=...&periodo_fim=...&id_leito=..."""
        periodo_inicio = request.args.get('periodo_inicio')
        periodo_fim = request.args.get('periodo_fim')
        id_leito = request.args.get('id_leito', type=int)

        if not periodo_inicio or not periodo_fim:
            return jsonify({"erro": "Par�metros 'periodo_inicio' e 'periodo_fim' s�o obrigat�rios"}), 400

        try:
            relatorio = VisitaService.relatorio_auditoria(periodo_inicio, periodo_fim, id_leito)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        return jsonify(relatorio), 200

    @classmethod
    @tratar_erros
    def relatorio_gerencial(cls):
        """sp_relatorio_gerencial_visitas: GET /relatorios/visitas?periodo_inicio=...&periodo_fim=...&id_paciente=..."""
        periodo_inicio = request.args.get('periodo_inicio')
        periodo_fim = request.args.get('periodo_fim')
        id_paciente = request.args.get('id_paciente', type=int)

        if not periodo_inicio or not periodo_fim:
            return jsonify({"erro": "Par�metros 'periodo_inicio' e 'periodo_fim' s�o obrigat�rios"}), 400

        try:
            relatorio = VisitaService.relatorio_gerencial(periodo_inicio, periodo_fim, id_paciente)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        return jsonify(relatorio), 200

    @classmethod
    @tratar_erros
    def proxima_vaga(cls, id):
        """sp_verificar_slot_extensao: GET /leitos/<id>/proxima-vaga?horario_agendado=..."""
        horario_agendado = request.args.get('horario_agendado')
        if not horario_agendado:
            return jsonify({"erro": "Par�metro 'horario_agendado' � obrigat�rio (ISO 8601)"}), 400

        try:
            disponivel = VisitaService.verificar_extensao(id, horario_agendado)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        return jsonify({"disponivel_para_extensao": disponivel}), 200

    @classmethod
    @tratar_erros
    def pode_gerar_qrcode(cls, id):
        """sp_validar_janela_qrcode: GET /visitas/<id>/pode-gerar-qrcode"""
        try:
            pode_gerar = VisitaService.validar_janela_qrcode(id)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 404

        return jsonify({"pode_gerar_qrcode": pode_gerar}), 200

    @classmethod
    @tratar_erros
    def validar_entrada_totem(cls):
        """sp_validar_entrada_totem: POST /totem/validar-entrada  body: {"codigo_qrcode": "..."}"""
        dados = request.get_json(silent=True)
        if not dados or not dados.get('codigo_qrcode'):
            return jsonify({"erro": "Campo 'codigo_qrcode' � obrigat�rio"}), 400

        resultado = VisitaService.validar_entrada(dados['codigo_qrcode'])
        status_http = 200 if resultado.get('liberado') else 403
        return jsonify(resultado), status_http

    @classmethod
    @tratar_erros
    def horarios_disponiveis(cls, id):
        """GET /internacoes/<id>/horarios?data=YYYY-MM-DD"""
        data_str = request.args.get('data')
        if not data_str:
            return jsonify({"erro": "Parâmetro 'data' é obrigatório (YYYY-MM-DD)"}), 400

        try:
            horarios = VisitaService.horarios_disponiveis(id, data_str)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        return jsonify(horarios), 200