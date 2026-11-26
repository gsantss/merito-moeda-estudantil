from fastapi import APIRouter, Depends, Request
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
    empresa = service.obter_ou_404(db, empresa_id)
    sessao = request.session.get('user_id')
    return service.apresentar(empresa, privado=(sessao == empresa.id))


@router.put('/{empresa_id}')
def atualizar(empresa_id: str, payload: EmpresaAtualizar, request: Request,
              db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, empresa_id, 'empresa')
    empresa = service.obter_ou_404(db, empresa_id)
    return {'mensagem': 'Empresa atualizada.', 'empresa': service.apresentar(service.atualizar(db, empresa, payload))}


@router.delete('/{empresa_id}')
def excluir(empresa_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, empresa_id, 'empresa')
    empresa = service.obter_ou_404(db, empresa_id)
    service.excluir(db, empresa)
    request.session.clear()
    return {'mensagem': 'Empresa excluída.'}


@router.patch('/{empresa_id}/desativar')
def desativar(empresa_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, empresa_id, 'empresa')
    service.desativar(db, usuario)
    request.session.clear()
    return {'mensagem': 'Conta desativada. Vantagens e comprovantes preservados.'}
