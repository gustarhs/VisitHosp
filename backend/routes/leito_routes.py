from flask import Blueprint
from controllers.controllers import LeitoController
 
leito_bp = Blueprint("leito_bp", __name__)
 
leito_bp.add_url_rule("/leitos", view_func=LeitoController.listar, methods=["GET"])
leito_bp.add_url_rule("/leitos/<int:id>", view_func=LeitoController.buscar, methods=["GET"])
leito_bp.add_url_rule("/leitos", view_func=LeitoController.cadastrar, methods=["POST"])
leito_bp.add_url_rule("/leitos/<int:id>", view_func=LeitoController.atualizar, methods=["PUT"])
leito_bp.add_url_rule("/leitos/<int:id>", view_func=LeitoController.excluir, methods=["DELETE"])