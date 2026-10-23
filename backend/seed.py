"""Popula o banco com dados de demonstracao.

Uso (dentro da pasta backend):
    python seed.py            -> so popula se o banco estiver vazio
    python seed.py --reset    -> APAGA todas as tabelas e popula de novo
"""
import sys

from app import app
from extensions import db
from database.seed import banco_vazio, popular_banco, imprimir_resumo

if __name__ == "__main__":
    with app.app_context():
        if "--reset" in sys.argv:
            if input("Isso APAGA todos os dados do banco. Digite SIM para continuar: ").strip() != "SIM":
                print("Cancelado.")
                sys.exit(0)
            db.drop_all()
            db.create_all()
            imprimir_resumo(popular_banco())
        elif banco_vazio():
            imprimir_resumo(popular_banco())
        else:
            print("O banco já possui dados. Use 'python seed.py --reset' para recriar do zero.")
