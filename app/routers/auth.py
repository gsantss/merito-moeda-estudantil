import secrets
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from app.schemas import LoginPayload
from app.security import exigir_csrf, verificar_senha

router = APIRouter(prefix='/api', tags=['Autenticação'])

@router.get('/sessao')
def sessao(request: Request, db: Session = Depends(get_db)):
    if 'csrf_token' not in request.session:
        request.session['csrf_token'] = secrets.token_urlsafe(32)
    uid = request.session.get('user_id')
    usuario = db.get(Usuario, uid) if uid else None
    if usuario is None or not usuario.ativo:
        request.session.pop('user_id', None)
        return {'autenticado': False, 'csrf_token': request.session['csrf_token']}
    perfil = usuario.aluno or usuario.professor or usuario.empresa
    return {'autenticado': True, 'id': usuario.id, 'perfil': usuario.perfil,
            'nome': perfil.nome if perfil else usuario.login, 'login': usuario.login,
            'csrf_token': request.session['csrf_token']}

@router.post('/auth/login')
def login(payload: LoginPayload, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = db.scalar(select(Usuario).where(Usuario.login == payload.login.strip().lower()))
    if not usuario or not usuario.ativo or not verificar_senha(payload.senha, usuario.senha_hash):
        raise HTTPException(401, 'Login ou senha inválidos.')
    # Rotação do token CSRF no início da sessão autenticada.
    request.session.clear()
    request.session['user_id'] = usuario.id
    request.session['csrf_token'] = secrets.token_urlsafe(32)
    return {'mensagem': 'Login realizado.', 'perfil': usuario.perfil, 'id': usuario.id,
            'csrf_token': request.session['csrf_token']}

@router.post('/auth/logout')
def logout(request: Request, _=Depends(exigir_csrf)):
    request.session.clear()
    return {'mensagem': 'Sessão encerrada.'}
