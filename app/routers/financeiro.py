from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import EmpresaParceira, Vantagem
from app.schemas_extra import VantagemCriar, DistribuicaoCriar, ResgateCriar, UsoCupom
from app.security import usuario_atual, exigir_perfil, exigir_csrf
from app.services import financeiro

router = APIRouter(prefix='/api', tags=['Vantagens, carteira e resgates'])

@router.get('/vantagens')
def vantagens(db: Session = Depends(get_db)):
    rows = db.execute(select(Vantagem, EmpresaParceira).join(
        EmpresaParceira, Vantagem.empresa_id == EmpresaParceira.id)
        .where(Vantagem.ativa.is_(True)).order_by(Vantagem.titulo)).all()
    return [apresentar_vantagem(v, e.nome) for v,e in rows]

def apresentar_vantagem(v: Vantagem, empresa_nome: str = ''):
    return {'id': v.id, 'empresa_id': v.empresa_id, 'empresa': empresa_nome,
            'titulo': v.titulo, 'descricao': v.descricao, 'foto_url': v.foto_url,
            'custo': v.custo, 'ativa': v.ativa}

@router.get('/vantagens/minhas')
def minhas_vantagens(request: Request, db: Session = Depends(get_db)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    return [apresentar_vantagem(v) for v in db.scalars(
        select(Vantagem).where(Vantagem.empresa_id == u.id).order_by(Vantagem.titulo)).all()]

@router.post('/vantagens', status_code=201)
def criar_vantagem(payload: VantagemCriar, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    v = Vantagem(empresa_id=u.id, **payload.model_dump())
    db.add(v); db.commit(); db.refresh(v)
    return apresentar_vantagem(v, u.empresa.nome)

@router.put('/vantagens/{vantagem_id}')
def editar_vantagem(vantagem_id: str, payload: VantagemCriar, request: Request,
                    db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    v = db.get(Vantagem, vantagem_id)
    if not v: raise HTTPException(404, 'Vantagem não encontrada.')
    if v.empresa_id != u.id: raise HTTPException(403, 'Você só pode editar vantagens próprias.')
    for k, value in payload.model_dump().items(): setattr(v, k, value)
    db.commit(); db.refresh(v)
    return apresentar_vantagem(v, u.empresa.nome)

@router.delete('/vantagens/{vantagem_id}')
def excluir_vantagem(vantagem_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    u = usuario_atual(request, db); exigir_perfil(u, 'empresa')
    v = db.get(Vantagem, vantagem_id)
    if not v: raise HTTPException(404, 'Vantagem não encontrada.')
    if v.empresa_id != u.id: raise HTTPException(403, 'Você só pode excluir vantagens próprias.')
    # Arquivamento preserva relação com resgates anteriores.
    v.ativa = False; db.commit()
    return {'mensagem': 'Vantagem desativada. Registros de resgates preservados.'}

@router.get('/extrato')
def extrato(request: Request, db: Session = Depends(get_db)):
    u = usuario_atual(request, db)
    if u.perfil not in ('aluno', 'professor'): raise HTTPException(403, 'Perfil sem carteira.')
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
