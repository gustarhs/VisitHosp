from flask import Blueprint
from controllers.controllers import VisitaController
 
visita_bp = Blueprint("visita_bp", __name__)
 
visita_bp.add_url_rule("/visitas", view_func=VisitaController.listar, methods=["GET"])
visita_bp.add_url_rule("/visitas/<int:id>", view_func=VisitaController.buscar, methods=["GET"])
visita_bp.add_url_rule("/visitas", view_func=VisitaController.cadastrar, methods=["POST"])
visita_bp.add_url_rule("/visitas/<int:id>", view_func=VisitaController.atualizar, methods=["PUT"])
visita_bp.add_url_rule("/visitas/<int:id>", view_func=VisitaController.excluir, methods=["DELETE"])