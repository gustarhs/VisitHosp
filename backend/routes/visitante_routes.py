from flask import Blueprint
from controllers import VisitanteController
 
visitante_bp = Blueprint("visitante_bp", __name__)
 
visitante_bp.add_url_rule("/visitantes", view_func=VisitanteController.listar, methods=["GET"])
visitante_bp.add_url_rule("/visitantes/<int:id>", view_func=VisitanteController.buscar, methods=["GET"])
visitante_bp.add_url_rule("/visitantes", view_func=VisitanteController.cadastrar, methods=["POST"])
visitante_bp.add_url_rule("/visitantes/<int:id>", view_func=VisitanteController.atualizar, methods=["PUT"])
visitante_bp.add_url_rule("/visitantes/<int:id>", view_func=VisitanteController.excluir, methods=["DELETE"])
visitante_bp.add_url_rule("/visitantes/<int:id>/revogar", view_func=VisitanteController.revogar, methods=["PUT"])
visitante_bp.add_url_rule("/visitantes/<int:id>/regras-acesso", view_func=VisitanteController.regras_acesso, methods=["GET"])
visitante_bp.add_url_rule("/visitantes/pendentes", view_func=VisitanteController.cadastros_pendentes, methods=["GET"])
