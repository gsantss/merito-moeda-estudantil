"""Autenticação com PBKDF2, sessão HTTPOnly e verificação de perfis."""
import hashlib
import hmac
import secrets
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from app.models import Usuario

ITERACOES = 390_000

def hash_senha(senha: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, ITERACOES)
    return f'pbkdf2_sha256${ITERACOES}${salt.hex()}${digest.hex()}'


def verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        algoritmo, iteracoes, salt, esperado = armazenado.split('$')
        if algoritmo != 'pbkdf2_sha256':
            return False
        obtido = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), bytes.fromhex(salt), int(iteracoes))
        return hmac.compare_digest(obtido, bytes.fromhex(esperado))
    except (ValueError, TypeError):
        return False


def usuario_atual(request: Request, db: Session) -> Usuario:
    uid = request.session.get('user_id')
    usuario = db.get(Usuario, uid) if uid else None
    if usuario is None or not usuario.ativo:
        raise HTTPException(status_code=401, detail='Faça login para continuar.')
    return usuario


def exigir_perfil(usuario: Usuario, perfil: str):
    if usuario.perfil != perfil:
        raise HTTPException(status_code=403, detail='Acesso negado para este perfil.')


def exigir_dono(usuario: Usuario, id_perfil: str, perfil: str):
    exigir_perfil(usuario, perfil)
    if usuario.id != id_perfil:
        raise HTTPException(status_code=403, detail='Você só pode alterar seu próprio cadastro.')


def exigir_csrf(request: Request):
    esperado = request.session.get('csrf_token')
    recebido = request.headers.get('x-csrf-token')
    if not esperado or not recebido or not hmac.compare_digest(esperado, recebido):
        raise HTTPException(status_code=403, detail='Sessão de segurança inválida. Atualize a página e tente novamente.')
