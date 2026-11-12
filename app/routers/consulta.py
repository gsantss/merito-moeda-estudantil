from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Instituicao
from app.security import usuario_atual

router = APIRouter(prefix='/api', tags=['Consultas'])

@router.get('/instituicoes')
def instituicoes(db: Session = Depends(get_db)):
    return [{'id': i.id, 'nome': i.nome} for i in db.scalars(
        select(Instituicao).where(Instituicao.ativa == True).order_by(Instituicao.nome)).all()]

@router.get('/carteira')
def carteira(request: Request, db: Session = Depends(get_db)):
    usuario = usuario_atual(request, db)
    return {'saldo': usuario.carteira.saldo if usuario.carteira else None,
            'perfil': usuario.perfil, 'mensagem': 'Carteira atualizada com movimentos registrados no extrato.'}
