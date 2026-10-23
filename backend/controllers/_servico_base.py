from functools import wraps

from flask import jsonify

from services.comum import ErroServico


def responder(func):
    """Converte erros de negocio (ErroServico) em JSON com o status HTTP correto."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ErroServico as e:
            return jsonify({"erro": str(e)}), e.status
        except Exception as e:
            return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    return wrapper
