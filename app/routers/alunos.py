from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Aluno
from app.schemas import AlunoCriar, AlunoAtualizar
from app.security import exigir_csrf, exigir_dono, usuario_atual
from app.services import alunos as service
from app.repositories import alunos as repo

router = APIRouter(prefix='/api/alunos', tags=['Alunos'])

@router.post('', status_code=201)
def criar(payload: AlunoCriar, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    aluno = service.criar(db, payload)
    return {'mensagem': 'Aluno cadastrado com sucesso.', 'aluno': service.apresentar(aluno)}

@router.get('')
def listar(request: Request, db: Session = Depends(get_db)):
    usuario = usuario_atual(request, db)
    if usuario.perfil == 'professor':
        return [service.apresentar(a, privado=False) for a in repo.por_instituicao(db, usuario.professor.instituicao_id)]
    if usuario.perfil == 'aluno':
        return [service.apresentar(usuario.aluno)]
    raise HTTPException(403, 'Lista de alunos restrita à instituição do professor.')

@router.get('/{aluno_id}')
def detalhar(aluno_id: str, request: Request, db: Session = Depends(get_db)):
    usuario = usuario_atual(request, db)
    aluno = repo.por_id(db, aluno_id)
    if not aluno:
        raise HTTPException(404, 'Aluno não encontrado.')
    if usuario.id == aluno.id and usuario.perfil == 'aluno':
        return service.apresentar(aluno)
    if usuario.perfil == 'professor' and usuario.professor.instituicao_id == aluno.instituicao_id:
        return service.apresentar(aluno, privado=False)
    raise HTTPException(403, 'Você não tem permissão para ver este cadastro.')

@router.put('/{aluno_id}')
def atualizar(aluno_id: str, payload: AlunoAtualizar, request: Request,
              db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, aluno_id, 'aluno')
    aluno = repo.por_id(db, aluno_id)
    if not aluno:
        raise HTTPException(404, 'Aluno não encontrado.')
    return {'mensagem': 'Cadastro atualizado.', 'aluno': service.apresentar(service.atualizar(db, aluno, payload))}

@router.delete('/{aluno_id}')
def excluir(aluno_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, aluno_id, 'aluno')
    aluno = repo.por_id(db, aluno_id)
    if not aluno:
        raise HTTPException(404, 'Aluno não encontrado.')
    service.excluir(db, aluno)
    request.session.clear()
    return {'mensagem': 'Cadastro excluído.'}

@router.patch('/{aluno_id}/desativar')
def desativar(aluno_id: str, request: Request, db: Session = Depends(get_db), _=Depends(exigir_csrf)):
    usuario = usuario_atual(request, db)
    exigir_dono(usuario, aluno_id, 'aluno')
    usuario.ativo = False
    db.commit()
    request.session.clear()
    return {'mensagem': 'Conta desativada. Histórico financeiro preservado.'}
