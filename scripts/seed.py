"""Executar manualmente: python -m scripts.seed"""
from app.database import Base, engine, SessionLocal
from app.models import *  # noqa: F401,F403  (importa metadados do ORM)
from app.seed import popular_banco

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        popular_banco(db)
    print('Pré-cadastro institucional verificado com sucesso.')
