import secrets
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LoginPayload
from app.security import exigir_csrf
from app.services import auth as auth_service

router = APIRouter(prefix='/api', tags=['Autenticação'])


@router.get('/sessao')
def sessao(request: Request, db: Session = Depends(get_db)):
    if 'csrf_token' not in request.session:
        request.session['csrf_token'] = secrets.token_urlsafe(32)
    usuario = auth_service.obter_usuario_ativo(db, request.session.get('user_id'))
    if usuario is None:
        request.session.pop('user_id', None)
        return {'autenticado': False, 'csrf_token': request.session['csrf_token']}
    return {'autenticado': True, 'id': usuario.id, 'perfil': usuario.perfil,
            'nome': usuario.nome_exibicao, 'login': usuario.login,
            'csrf_token': request.session['csrf_token']}


@router.post('/auth/login')
def login(payload: LoginPayload, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = auth_service.autenticar(db, payload.login, payload.senha)
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
