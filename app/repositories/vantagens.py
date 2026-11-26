"""Acesso a dados para vantagens parceiras."""
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models import EmpresaParceira, Vantagem


def por_id(db: Session, vantagem_id: str) -> Vantagem | None:
    return db.get(Vantagem, vantagem_id)


def listar_ativas_com_empresa(db: Session):
    return db.execute(
        select(Vantagem, EmpresaParceira)
        .join(EmpresaParceira, Vantagem.empresa_id == EmpresaParceira.id)
        .where(Vantagem.ativa.is_(True))
        .order_by(Vantagem.titulo)
    ).all()


def por_empresa(db: Session, empresa_id: str):
    return db.scalars(
        select(Vantagem).where(Vantagem.empresa_id == empresa_id).order_by(Vantagem.titulo)
    ).all()


def existe_por_empresa(db: Session, empresa_id: str) -> bool:
    return db.scalar(
        select(Vantagem.id).where(Vantagem.empresa_id == empresa_id).limit(1)
    ) is not None


def desativar_por_empresa(db: Session, empresa_id: str) -> None:
    db.execute(update(Vantagem).where(Vantagem.empresa_id == empresa_id).values(ativa=False))
