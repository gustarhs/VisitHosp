from flask import Blueprint
from controllers import PacienteController
 
paciente_bp = Blueprint("paciente_bp", __name__)
 
paciente_bp.add_url_rule("/pacientes", view_func=PacienteController.listar, methods=["GET"])
paciente_bp.add_url_rule("/pacientes/<int:id>", view_func=PacienteController.buscar, methods=["GET"])
paciente_bp.add_url_rule("/pacientes", view_func=PacienteController.cadastrar, methods=["POST"])
paciente_bp.add_url_rule("/pacientes/<int:id>", view_func=PacienteController.atualizar, methods=["PUT"])
paciente_bp.add_url_rule("/pacientes/<int:id>", view_func=PacienteController.excluir, methods=["DELETE"])
paciente_bp.add_url_rule("/pacientes/<int:id>/bloqueio", view_func=PacienteController.bloqueio_status, methods=["GET"])
paciente_bp.add_url_rule("/pacientes/<int:id>/responsavel", view_func=PacienteController.responsavel_autorizado, methods=["GET"])
