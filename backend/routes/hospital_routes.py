from flask import Blueprint
from controllers.controllers import HospitalController
 
hospital_bp = Blueprint("hospital_bp", __name__)
 
hospital_bp.add_url_rule("/hospitais", view_func=HospitalController.listar, methods=["GET"])
hospital_bp.add_url_rule("/hospitais/<int:id>", view_func=HospitalController.buscar, methods=["GET"])
hospital_bp.add_url_rule("/hospitais", view_func=HospitalController.cadastrar, methods=["POST"])
hospital_bp.add_url_rule("/hospitais/<int:id>", view_func=HospitalController.atualizar, methods=["PUT"])
hospital_bp.add_url_rule("/hospitais/<int:id>", view_func=HospitalController.excluir, methods=["DELETE"])