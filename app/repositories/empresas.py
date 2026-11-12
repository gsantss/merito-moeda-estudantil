from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import EmpresaParceira

def por_id(db: Session, uid: str):
    return db.get(EmpresaParceira, uid)

def listar(db: Session):
    return db.scalars(select(EmpresaParceira).order_by(EmpresaParceira.nome)).all()

def por_email(db: Session, email: str):
    return db.scalar(select(EmpresaParceira).where(EmpresaParceira.email_contato == email))

def por_cnpj(db: Session, cnpj: str):
    return db.scalar(select(EmpresaParceira).where(EmpresaParceira.cnpj == cnpj))
