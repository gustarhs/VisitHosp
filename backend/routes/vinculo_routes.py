from flask import Blueprint
from controllers.vinculo_controller import VinculoController

vinculo_bp = Blueprint("vinculo_bp", __name__)

vinculo_bp.add_url_rule("/visitantes/cadastro-vinculado", view_func=VinculoController.cadastrar, methods=["POST"])
vinculo_bp.add_url_rule("/pacientes/<int:id>/visitantes", view_func=VinculoController.listar_por_paciente, methods=["GET"])
vinculo_bp.add_url_rule("/visitantes/<int:id>/revogar-acesso", view_func=VinculoController.revogar, methods=["POST"])
