from datetime import datetime
from functools import wraps
from flask import jsonify


def parse_datetime(valor):
    """
    Tenta converter uma string ISO 8601 em um objeto datetime.
    Retorna None se a conversão falhar ou o valor for vazio.
    """
    if not valor:
        return None
    try:
        # Aceita tanto 'YYYY-MM-DD' quanto formatos ISO completos
        return datetime.fromisoformat(valor.replace('Z', '+00:00'))
    except (ValueError, TypeError, AttributeError):
        return None


def campos_faltando(dados, obrigatorios):
    """
    Recebe um dicionário 'dados' e uma lista de chaves obrigatórias.
    Retorna a lista de chaves que estão ausentes ou vazias (None).
    """
    faltando = []
    for campo in obrigatorios:
        if campo not in dados or dados[campo] in (None, ''):
            faltando.append(campo)
    return faltando


def tratar_erros(func):
    """
    Decorator para capturar exceções não previstas nos métodos do controller
    e retornar uma resposta JSON padronizada em vez de estourar um 500 cru.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    return wrapper