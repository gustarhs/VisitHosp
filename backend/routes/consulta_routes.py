from flask import Blueprint
from controllers.consulta_controller import ConsultaController

consulta_bp = Blueprint("consulta_bp", __name__)

consulta_bp.add_url_rule("/regulamento", view_func=ConsultaController.regulamento, methods=["GET"])
consulta_bp.add_url_rule("/pacientes/<int:id>/status", view_func=ConsultaController.status_paciente, methods=["GET"])
consulta_bp.add_url_rule("/leitos/<int:id>/localizacao", view_func=ConsultaController.localizacao_leito, methods=["GET"])
consulta_bp.add_url_rule("/leitos/<int:id>/horarios-ocupados", view_func=ConsultaController.horarios_ocupados_leito, methods=["GET"])
