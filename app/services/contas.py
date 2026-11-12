from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Usuario, Instituicao

def checar_login(db: Session, login: str, exceto: str | None = None):
    existente = db.scalar(select(Usuario).where(Usuario.login == login.lower()))
    if existente and existente.id != exceto:
        raise HTTPException(409, 'Esse login já está sendo usado.')

def validar_instituicao(db: Session, id: str):
    inst = db.get(Instituicao, id)
    if not inst or not inst.ativa:
        raise HTTPException(422, 'Selecione uma instituição ativa e cadastrada.')
    return inst

def conflito(erro):
    # Não expõe o SQL nem dados pessoais em respostas HTTP.
    raise HTTPException(409, 'Há conflito com um cadastro existente. Confira login, e-mail e documentos.') from erro
