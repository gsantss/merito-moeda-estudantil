from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Aluno, Usuario

def por_id(db: Session, uid: str):
    return db.get(Aluno, uid)

def por_instituicao(db: Session, instituicao_id: str):
    return db.scalars(select(Aluno).where(Aluno.instituicao_id == instituicao_id).order_by(Aluno.nome)).all()

def por_email(db: Session, email: str):
    return db.scalar(select(Aluno).where(Aluno.email == email))

def por_cpf(db: Session, cpf: str):
    return db.scalar(select(Aluno).where(Aluno.cpf == cpf))
