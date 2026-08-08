from flask import Blueprint
from controllers.controllers import VisitanteController
 
visitante_bp = Blueprint("visitante_bp", __name__)
 
visitante_bp.add_url_rule("/visitantes", view_func=VisitanteController.listar, methods=["GET"])
visitante_bp.add_url_rule("/visitantes/<int:id>", view_func=VisitanteController.buscar, methods=["GET"])
visitante_bp.add_url_rule("/visitantes", view_func=VisitanteController.cadastrar, methods=["POST"])
visitante_bp.add_url_rule("/visitantes/<int:id>", view_func=VisitanteController.atualizar, methods=["PUT"])
visitante_bp.add_url_rule("/visitantes/<int:id>", view_func=VisitanteController.excluir, methods=["DELETE"])
 