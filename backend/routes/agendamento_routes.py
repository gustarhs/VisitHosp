from flask import Blueprint
from controllers.agendamento_controller import AgendamentoController

agendamento_bp = Blueprint("agendamento_bp", __name__)

agendamento_bp.add_url_rule("/internacoes/<int:id>/visitas", view_func=AgendamentoController.listar_por_internacao, methods=["GET"])
agendamento_bp.add_url_rule("/visitas/<int:id>/cancelar", view_func=AgendamentoController.cancelar, methods=["POST"])
agendamento_bp.add_url_rule("/visitas/<int:id>/reagendar", view_func=AgendamentoController.reagendar, methods=["POST"])
