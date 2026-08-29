from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db
from routes import hospital_bp, paciente_bp, visitante_bp, leito_bp, triagem_bp, internacao_bp, visita_bp, upload_bp

app = Flask(__name__)

app.config.from_object(Config)

CORS(app, origins=["http://localhost:5500"])

db.init_app(app)

app.register_blueprint(hospital_bp)
app.register_blueprint(paciente_bp)
app.register_blueprint(visitante_bp)
app.register_blueprint(leito_bp)
app.register_blueprint(triagem_bp)
app.register_blueprint(internacao_bp)
app.register_blueprint(visita_bp)
app.register_blueprint(upload_bp)

with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)