from .hospital_routes import hospital_bp
from .paciente_routes import paciente_bp
from .internacao_routes import internacao_bp
from .leito_routes import leito_bp
from .triagem_routes import triagem_bp
from .visitante_routes import visitante_bp
from .visita_routes import visita_bp
from .upload_routes import upload_bp

__all__ = [
    "hospital_bp",
    "paciente_bp",
    "internacao_bp",
    "leito_bp",
    "triagem_bp",
    "visitante_bp",
    "visita_bp",
    "upload_bp",
]