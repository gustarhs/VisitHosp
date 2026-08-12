from flask import Flask

from config import Config
from extensions import db
from routes import hospital_bp, paciente_bp, visitante_bp, leito_bp, triagem_bp, internacao_bp, visita_bp

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
