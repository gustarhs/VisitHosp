import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory

upload_bp = Blueprint("upload_bp", __name__)

PASTA_UPLOADS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(PASTA_UPLOADS, exist_ok=True)

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "pdf"}


def extensao_permitida(nome_arquivo):
    return "." in nome_arquivo and nome_arquivo.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS


@upload_bp.route("/uploads", methods=["POST"])
def upload_documento():
    if "arquivo" not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado. Envie no campo 'arquivo'."}), 400

    arquivo = request.files["arquivo"]

    if arquivo.filename == "":
        return jsonify({"erro": "Nenhum arquivo selecionado."}), 400

    if not extensao_permitida(arquivo.filename):
        return jsonify({"erro": "Tipo de arquivo não permitido. Use PNG, JPG ou PDF."}), 400

    extensao = arquivo.filename.rsplit(".", 1)[1].lower()
    nome_unico = f"{uuid.uuid4().hex}.{extensao}"
    caminho = os.path.join(PASTA_UPLOADS, nome_unico)
    arquivo.save(caminho)

    return jsonify({
        "arquivo": nome_unico,
        "nome_original": arquivo.filename,
        "url": f"/uploads/{nome_unico}"
    }), 201


@upload_bp.route("/uploads/<path:nome_arquivo>", methods=["GET"])
def servir_upload(nome_arquivo):
    return send_from_directory(PASTA_UPLOADS, nome_arquivo)