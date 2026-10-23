from flask import Blueprint
from controllers.acesso_controller import AcessoController

acesso_bp = Blueprint("acesso_bp", __name__)

acesso_bp.add_url_rule("/visitas/<int:id>/checkin", view_func=AcessoController.checkin, methods=["POST"])
acesso_bp.add_url_rule("/visitas/<int:id>/checkout", view_func=AcessoController.checkout, methods=["POST"])
acesso_bp.add_url_rule("/relatorios/historico-visitas", view_func=AcessoController.historico_visitas, methods=["GET"])
acesso_bp.add_url_rule("/relatorios/auditoria-acessos", view_func=AcessoController.auditoria_acessos, methods=["GET"])
acesso_bp.add_url_rule("/relatorios/visitantes-por-turno", view_func=AcessoController.visitantes_por_turno, methods=["GET"])
