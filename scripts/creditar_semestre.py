"""Execute no início de cada semestre, via cron/Agendador de Tarefas.

Ex.: python -m scripts.creditar_semestre 2026/2
"""
import argparse
from app.database import Base, engine, SessionLocal
from app.models import *  # noqa - registra ORM
from app.seed import popular_banco
from app.services.financeiro import creditos_semestre

def main():
    parser = argparse.ArgumentParser(description='Crédito de 1000 moedas por professor e semestre.')
    parser.add_argument('semestre', help='AAAA/1 ou AAAA/2')
    args = parser.parse_args()
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        popular_banco(db)
        print(creditos_semestre(db, args.semestre))

if __name__ == '__main__': main()
