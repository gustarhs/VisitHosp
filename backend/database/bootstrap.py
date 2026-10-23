"""
Prepara o MySQL antes do Flask subir:
  - confere se o servidor esta acessivel com as credenciais do .env
  - cria o banco (DB_NAME) caso ainda nao exista
Antes disso o projeto quebrava com "Unknown database 'db_visithosp'" e nao iniciava.
"""
import os
import re
import sys

import pymysql


def _sair(mensagem):
    print("\n" + "=" * 70)
    print("NÃO FOI POSSÍVEL CONECTAR AO BANCO DE DADOS")
    print("=" * 70)
    print(mensagem)
    print("=" * 70 + "\n")
    sys.exit(1)


def garantir_banco():
    host = os.getenv("DB_HOST", "localhost")
    usuario = os.getenv("DB_USER", "root")
    senha = os.getenv("DB_PASSWORD", "")
    banco = os.getenv("DB_NAME", "db_visithosp")

    if not re.fullmatch(r"[A-Za-z0-9_]+", banco):
        _sair(f"DB_NAME inválido no .env: '{banco}'. Use apenas letras, números e _.")

    try:
        conexao = pymysql.connect(host=host, user=usuario, password=senha)
    except pymysql.err.OperationalError as e:
        codigo = e.args[0] if e.args else None
        if codigo == 2003:
            _sair(f"O servidor MySQL não está respondendo em '{host}'.\n"
                  "-> Inicie o MySQL (serviço MySQL80 no Windows) e tente de novo.")
        if codigo == 1045:
            _sair(f"Usuário ou senha incorretos para '{usuario}'@'{host}'.\n"
                  "-> Confira DB_USER e DB_PASSWORD no arquivo .env (na raiz do projeto).")
        _sair(f"Erro do MySQL: {e}")
    except RuntimeError as e:
        # PyMySQL levanta RuntimeError quando falta o pacote 'cryptography' (MySQL 8)
        _sair(f"{e}\n-> Rode:  pip install cryptography")

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{banco}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conexao.commit()
    except pymysql.MySQLError as e:
        _sair(f"Não foi possível criar o banco '{banco}': {e}")
    finally:
        conexao.close()
