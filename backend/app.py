from flask import Flask

from config import Config
from extensions import db

from controllers.hospital_controller import hospital_bp
from controllers.paciente_controller import paciente_bp
from controllers.visitante_controller import visitante_bp
from controllers.leito_controller import leito_bp
from controllers.triagem_controller import triagem_bp
from controllers.internacao_controller import internacao_bp
from controllers.visita_controller import visita_bp


app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(hospital_bp)
app.register_blueprint(paciente_bp)
app.register_blueprint(visitante_bp)
app.register_blueprint(leito_bp)
app.register_blueprint(triagem_bp)
app.register_blueprint(internacao_bp)
app.register_blueprint(visita_bp)

with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run()