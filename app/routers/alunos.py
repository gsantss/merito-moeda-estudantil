from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AlunoCriar, AlunoAtualizar
from app.security import exigir_csrf, exigir_dono, usuario_atual
from app.services import alunos as service

router = APIRouter(prefix='/api/alunos', tags=['Alunos'])


@router.post('', status_code=201)
def criar(payload: AlunoCriar, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    aluno = service.criar(db, payload)
    return {'mensagem': 'Aluno cadastrado com sucesso.', 'aluno': service.apresentar(aluno)}


@router.get('')
def listar(request: Request, db: Session = Depends(get_db)):
    usuario = usuario_atual(request, db)
    return service.listar_para(db, usuario)


@router.get('/{aluno_id}')
def detalhar(aluno_id: str, request: Request, db: Session = Depends(get_db)):
    usuario = usuario_atual(request, db)
    return service.detalhar_para(db, usuario, aluno_id)


@router.put('/{aluno_id}')
def atualizar(aluno_id: str, payload: AlunoAtualizar, request: Request,
              db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, aluno_id, 'aluno')
    aluno = service.obter_ou_404(db, aluno_id)
    return {'mensagem': 'Cadastro atualizado.', 'aluno': service.apresentar(service.atualizar(db, aluno, payload))}


@router.delete('/{aluno_id}')
def excluir(aluno_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, aluno_id, 'aluno')
    aluno = service.obter_ou_404(db, aluno_id)
    service.excluir(db, aluno)
    request.session.clear()
    return {'mensagem': 'Cadastro excluído.'}


@router.patch('/{aluno_id}/desativar')
def desativar(aluno_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, aluno_id, 'aluno')
    service.desativar(db, usuario)
    request.session.clear()
    return {'mensagem': 'Conta desativada. Histórico financeiro preservado.'}
