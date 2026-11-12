from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import EmpresaParceira, Usuario, Vantagem
from app.schemas import EmpresaCriar, EmpresaAtualizar
from app.security import hash_senha
from app.repositories import empresas as repo
from app.services.contas import checar_login, conflito


def apresentar(e: EmpresaParceira, *, privado: bool = True):
    resultado = {'id': e.id, 'nome': e.nome, 'descricao': e.descricao}
    if privado:
        resultado.update(email_contato=e.email_contato, cnpj=e.cnpj, login=e.usuario.login)
    return resultado


def _validar_contato(db, email, cnpj, exceto=None):
    outro = repo.por_email(db, email)
    if outro and outro.id != exceto:
        raise HTTPException(409, 'E-mail de contato já utilizado.')
    if cnpj:
        outro = repo.por_cnpj(db, cnpj)
        if outro and outro.id != exceto:
            raise HTTPException(409, 'CNPJ já cadastrado.')


def criar(db: Session, payload: EmpresaCriar):
    checar_login(db, payload.login.lower())
    _validar_contato(db, payload.email_contato, payload.cnpj)
    try:
        usuario = Usuario(login=payload.login.lower(), senha_hash=hash_senha(payload.senha), perfil='empresa')
        db.add(usuario)
        db.flush()
        empresa = EmpresaParceira(id=usuario.id, nome=payload.nome, email_contato=payload.email_contato,
                                  cnpj=payload.cnpj, descricao=payload.descricao)
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        return empresa
    except IntegrityError as e:
        db.rollback()
        conflito(e)


def atualizar(db: Session, empresa: EmpresaParceira, payload: EmpresaAtualizar):
    _validar_contato(db, payload.email_contato, payload.cnpj, empresa.id)
    try:
        for campo in ('nome','email_contato','cnpj','descricao'):
            setattr(empresa, campo, getattr(payload, campo))
        if payload.senha_nova:
            empresa.usuario.senha_hash = hash_senha(payload.senha_nova)
        db.commit()
        db.refresh(empresa)
        return empresa
    except IntegrityError as e:
        db.rollback()
        conflito(e)


def excluir(db: Session, empresa: EmpresaParceira):
    if db.query(Vantagem.id).filter(Vantagem.empresa_id == empresa.id).first():
        raise HTTPException(409, 'Empresa com vantagens cadastradas não pode ser excluída.')
    try:
        db.delete(empresa)
        db.delete(empresa.usuario)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(409, 'Empresa possui vínculos e não pode ser excluída.') from e
