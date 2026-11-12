"""Pré-cadastro idempotente das instituições e professor de demonstração."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Instituicao, Usuario, Professor, Carteira
from app.security import hash_senha
from app.config import SEED_DEMO_PROFESSOR

INSTITUICOES = (
    'PUC Minas',
    'Instituição Parceira Exemplo',
)

def popular_banco(db: Session):
    for nome in INSTITUICOES:
        if not db.scalar(select(Instituicao).where(Instituicao.nome == nome)):
            db.add(Instituicao(nome=nome))
    db.commit()
    if not SEED_DEMO_PROFESSOR:
        return
    if db.scalar(select(Usuario).where(Usuario.login == 'professor@demo.local')):
        return
    puc = db.scalar(select(Instituicao).where(Instituicao.nome == 'PUC Minas'))
    usuario = Usuario(login='professor@demo.local', senha_hash=hash_senha('Demo@12345'), perfil='professor')
    db.add(usuario)
    db.flush()
    db.add_all([
        Professor(id=usuario.id, nome='Professor Demonstração', cpf='00000000000',
                  departamento='Engenharia de Software', instituicao_id=puc.id),
        Carteira(usuario_id=usuario.id, saldo=0),
    ])
    db.commit()
