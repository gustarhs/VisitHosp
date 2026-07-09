from flask import Blueprint

registar_pb = Blueprint('registrar', __name__)
# Como se fosse um app route
registar_pb.route('/visitante/', methods = ['POST'])(criar_usuario)
registar_pb.route('/paciente/', methods = ['POST'])(criar_usuario)
registar_pb.route('/hospital/', methods = ['POST'])(criar_usuario)
