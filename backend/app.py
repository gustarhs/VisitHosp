import os

from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db
from database.bootstrap import garantir_banco
from database.seed import banco_vazio, popular_banco, imprimir_resumo
from routes import (
    hospital_bp, paciente_bp, visitante_bp, leito_bp, triagem_bp, internacao_bp, visita_bp, upload_bp,
    consulta_bp, agendamento_bp, vinculo_bp, acesso_bp,
)

# Cria o banco (db_visithosp) automaticamente caso ainda nao exista.
# Antes disso o app quebrava com "Unknown database" e nao iniciava.
garantir_banco()

app = Flask(__name__)

app.config.from_object(Config)

CORS(app, origins=[
    "http://localhost:5500", "http://127.0.0.1:5500",
    "http://localhost:5501", "http://127.0.0.1:5501",
])

db.init_app(app)

app.register_blueprint(hospital_bp)
app.register_blueprint(paciente_bp)
app.register_blueprint(visitante_bp)
app.register_blueprint(leito_bp)
app.register_blueprint(triagem_bp)
app.register_blueprint(internacao_bp)
app.register_blueprint(visita_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(consulta_bp)
app.register_blueprint(agendamento_bp)
app.register_blueprint(vinculo_bp)
app.register_blueprint(acesso_bp)

with app.app_context():
    db.create_all()

    # Banco vazio: carrega dados de demonstracao (hospital, leitos, pacientes, tokens, visitas).
    # Para desligar, coloque AUTO_SEED=0 no arquivo .env
    if os.getenv("AUTO_SEED", "1") != "0" and banco_vazio():
        imprimir_resumo(popular_banco())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)