from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas_extra import VantagemCriar, DistribuicaoCriar, ResgateCriar, UsoCupom
from app.security import usuario_atual, exigir_perfil, exigir_csrf
from app.services import financeiro, vantagens as vantagens_service

router = APIRouter(prefix='/api', tags=['Vantagens, carteira e resgates'])


def apresentar_vantagem(v, empresa_nome: str = ''):
    return vantagens_service.apresentar(v, empresa_nome)


@router.get('/vantagens')
def vantagens(db: Session = Depends(get_db)):
    return vantagens_service.listar_ativas(db)


@router.get('/vantagens/minhas')
def minhas_vantagens(request: Request, db: Session = Depends(get_db)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    return vantagens_service.listar_da_empresa(db, u.id)


@router.post('/vantagens', status_code=201)
def criar_vantagem(payload: VantagemCriar, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    return vantagens_service.criar(db, u.empresa, payload)


@router.put('/vantagens/{vantagem_id}')
def editar_vantagem(vantagem_id: str, payload: VantagemCriar, request: Request,
                    db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    return vantagens_service.atualizar(db, u.empresa, vantagem_id, payload)


@router.delete('/vantagens/{vantagem_id}')
def excluir_vantagem(vantagem_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    return vantagens_service.desativar(db, u.id, vantagem_id)

@router.get('/extrato')
def extrato(request: Request, db: Session = Depends(get_db)):
    u = usuario_atual(request, db)
    if not u.possui_carteira():
        raise HTTPException(403, 'Perfil sem carteira.')
    return financeiro.extrato(db, u.id)

@router.post('/distribuicoes', status_code=201)
def distribuir(payload: DistribuicaoCriar, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    u = usuario_atual(request, db); exigir_perfil(u, 'professor')
    return financeiro.distribuir(db, u.id, payload.aluno_id, payload.quantidade, payload.motivo)

@router.post('/resgates', status_code=201)
def resgatar(payload: ResgateCriar, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    u = usuario_atual(request, db); exigir_perfil(u, 'aluno')
    return financeiro.resgatar(db, u.id, payload.vantagem_id)

@router.get('/cupons')
def cupons(request: Request, db: Session = Depends(get_db)):
    u = usuario_atual(request, db); exigir_perfil(u, 'aluno')
    return financeiro.listar_cupons(db, u.id)

@router.get('/cupons/conferir/{codigo}')
def conferir_cupom(codigo: str, request: Request, db: Session = Depends(get_db)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    return financeiro.validar_cupom(db, u.id, codigo)

@router.post('/cupons/utilizar')
def utilizar_cupom(payload: UsoCupom, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    return financeiro.validar_cupom(db, u.id, payload.codigo, consumir=True)
