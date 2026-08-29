from flask import Blueprint
from controllers import VisitaController
 
visita_bp = Blueprint("visita_bp", __name__)
 
visita_bp.add_url_rule("/visitas", view_func=VisitaController.listar, methods=["GET"])
visita_bp.add_url_rule("/visitas/<int:id>", view_func=VisitaController.buscar, methods=["GET"])
visita_bp.add_url_rule("/visitas", view_func=VisitaController.cadastrar, methods=["POST"])
visita_bp.add_url_rule("/visitas/<int:id>", view_func=VisitaController.atualizar, methods=["PUT"])
visita_bp.add_url_rule("/visitas/<int:id>", view_func=VisitaController.excluir, methods=["DELETE"])
visita_bp.add_url_rule("/pacientes/<int:id>/visitas", view_func=VisitaController.historico_paciente, methods=["GET"])
visita_bp.add_url_rule("/relatorios/auditoria-fluxo", view_func=VisitaController.relatorio_auditoria_fluxo, methods=["GET"])
visita_bp.add_url_rule("/relatorios/visitas", view_func=VisitaController.relatorio_gerencial, methods=["GET"])
visita_bp.add_url_rule("/leitos/<int:id>/proxima-vaga", view_func=VisitaController.proxima_vaga, methods=["GET"])
visita_bp.add_url_rule("/visitas/<int:id>/pode-gerar-qrcode", view_func=VisitaController.pode_gerar_qrcode, methods=["GET"])
visita_bp.add_url_rule("/totem/validar-entrada", view_func=VisitaController.validar_entrada_totem, methods=["POST"])
visita_bp.add_url_rule("/internacoes/<int:id>/horarios", view_func=VisitaController.horarios_disponiveis, methods=["GET"])