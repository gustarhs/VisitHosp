from flask import Blueprint
from controllers.controllers import TriagemController
 
triagem_bp = Blueprint("triagem_bp", __name__)
 
triagem_bp.add_url_rule("/triagens", view_func=TriagemController.listar, methods=["GET"])
triagem_bp.add_url_rule("/triagens/<int:id>", view_func=TriagemController.buscar, methods=["GET"])
triagem_bp.add_url_rule("/triagens", view_func=TriagemController.cadastrar, methods=["POST"])
triagem_bp.add_url_rule("/triagens/<int:id>", view_func=TriagemController.atualizar, methods=["PUT"])
triagem_bp.add_url_rule("/triagens/<int:id>", view_func=TriagemController.excluir, methods=["DELETE"])
 