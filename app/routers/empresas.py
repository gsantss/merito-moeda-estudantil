from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import EmpresaCriar, EmpresaAtualizar
from app.security import exigir_csrf, exigir_dono, usuario_atual
from app.services import empresas as service
from app.repositories import empresas as repo

router = APIRouter(prefix='/api/empresas', tags=['Empresas parceiras'])

@router.post('', status_code=201)
def criar(payload: EmpresaCriar, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    empresa = service.criar(db, payload)
    return {'mensagem': 'Empresa cadastrada com sucesso.', 'empresa': service.apresentar(empresa)}

@router.get('')
def listar(db: Session = Depends(get_db)):
    return [service.apresentar(e, privado=False) for e in repo.listar(db)]

@router.get('/{empresa_id}')
def detalhar(empresa_id: str, request: Request, db: Session = Depends(get_db)):
    empresa = repo.por_id(db, empresa_id)
    if not empresa:
        raise HTTPException(404, 'Empresa não encontrada.')
    sessao = request.session.get('user_id')
    return service.apresentar(empresa, privado=(sessao == empresa.id))

@router.put('/{empresa_id}')
def atualizar(empresa_id: str, payload: EmpresaAtualizar, request: Request,
              db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, empresa_id, 'empresa')
    empresa = repo.por_id(db, empresa_id)
    if not empresa:
        raise HTTPException(404, 'Empresa não encontrada.')
    return {'mensagem': 'Empresa atualizada.', 'empresa': service.apresentar(service.atualizar(db, empresa, payload))}

@router.delete('/{empresa_id}')
def excluir(empresa_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, empresa_id, 'empresa')
    empresa = repo.por_id(db, empresa_id)
    if not empresa:
        raise HTTPException(404, 'Empresa não encontrada.')
    service.excluir(db, empresa)
    request.session.clear()
    return {'mensagem': 'Empresa excluída.'}

@router.patch('/{empresa_id}/desativar')
def desativar(empresa_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, empresa_id, 'empresa')
    usuario.ativo = False
    from sqlalchemy import update
    from app.models import Vantagem
    db.execute(update(Vantagem).where(Vantagem.empresa_id == empresa_id).values(ativa=False))
    db.commit()
    request.session.clear()
    return {'mensagem': 'Conta desativada. Vantagens e comprovantes preservados.'}
