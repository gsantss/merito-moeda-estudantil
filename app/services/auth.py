"""Serviço de autenticação e resolução do usuário da sessão."""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Usuario
from app.security import verificar_senha


def obter_usuario_ativo(db: Session, usuario_id: str | None) -> Usuario | None:
    """Retorna o usuário apenas se existir e estiver ativo."""
    if not usuario_id:
        return None
    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        return None
    return usuario


def autenticar(db: Session, login: str, senha: str) -> Usuario:
    """Valida credenciais e estado ativo do usuário, retornando HTTP 401 se inválido."""
    usuario = db.scalar(select(Usuario).where(Usuario.login == login.strip().lower()))
    if not usuario or not usuario.ativo or not verificar_senha(senha, usuario.senha_hash):
        raise HTTPException(401, 'Login ou senha inválidos.')
    return usuario
