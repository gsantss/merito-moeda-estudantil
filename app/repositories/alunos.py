from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.models import Aluno, Resgate, TransacaoMoedas


def por_id(db: Session, uid: str):
    return db.get(Aluno, uid)


def por_instituicao(db: Session, instituicao_id: str):
    return db.scalars(select(Aluno).where(Aluno.instituicao_id == instituicao_id).order_by(Aluno.nome)).all()


def por_email(db: Session, email: str):
    return db.scalar(select(Aluno).where(Aluno.email == email))


def por_cpf(db: Session, cpf: str):
    return db.scalar(select(Aluno).where(Aluno.cpf == cpf))


def possui_movimentacoes(db: Session, carteira_id: str) -> bool:
    return db.scalar(
        select(TransacaoMoedas.id)
        .where(or_(
            TransacaoMoedas.origem_carteira_id == carteira_id,
            TransacaoMoedas.destino_carteira_id == carteira_id,
        ))
        .limit(1)
    ) is not None


def possui_resgates(db: Session, aluno_id: str) -> bool:
    return db.scalar(select(Resgate.id).where(Resgate.aluno_id == aluno_id).limit(1)) is not None
