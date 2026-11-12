"""Crédito manual de 1.000 moedas por professor e semestre (idempotente).

Ex.: python -m scripts.creditar_semestre 2026/2   (sem argumento: semestre atual)
Na nuvem, a própria API executa o crédito do semestre atual automaticamente (app/tarefas.py).
"""
import argparse
from app.database import Base, engine, SessionLocal
from app.models import *  # noqa - registra ORM
from app.seed import popular_banco
from app.services.financeiro import creditos_semestre
from app.tarefas import semestre_atual

def main():
    parser = argparse.ArgumentParser(description='Crédito de 1000 moedas por professor e semestre.')
    parser.add_argument('semestre', nargs='?', default=semestre_atual(), help='AAAA/1 ou AAAA/2 (padrão: semestre atual)')
    args = parser.parse_args()
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        popular_banco(db)
        print(creditos_semestre(db, args.semestre))

if __name__ == '__main__': main()
