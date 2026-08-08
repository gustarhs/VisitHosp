from flask import Blueprint
from controllers.controllers import InternacaoController
 
internacao_bp = Blueprint("internacao_bp", __name__)
 
internacao_bp.add_url_rule("/internacoes", view_func=InternacaoController.listar, methods=["GET"])
internacao_bp.add_url_rule("/internacoes/<int:id>", view_func=InternacaoController.buscar, methods=["GET"])
internacao_bp.add_url_rule("/internacoes", view_func=InternacaoController.cadastrar, methods=["POST"])
internacao_bp.add_url_rule("/internacoes/<int:id>", view_func=InternacaoController.atualizar, methods=["PUT"])
internacao_bp.add_url_rule("/internacoes/<int:id>", view_func=InternacaoController.excluir, methods=["DELETE"])