from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import Aluno, Usuario, Carteira, Vantagem, Resgate
from app.schemas import AlunoCriar, AlunoAtualizar
from app.security import hash_senha
from app.repositories import alunos as repo
from app.services.contas import checar_login, validar_instituicao, conflito


def apresentar(a: Aluno, *, privado: bool = True):
    retorno = {
        'id': a.id, 'nome': a.nome, 'curso': a.curso,
        'instituicao_id': a.instituicao_id,
        'instituicao': a.instituicao.nome,
    }
    if privado:
        retorno.update(email=a.email, cpf=a.cpf, rg=a.rg, endereco=a.endereco, login=a.usuario.login)
    return retorno


def criar(db: Session, payload: AlunoCriar):
    validar_instituicao(db, payload.instituicao_id)
    checar_login(db, payload.login.lower())
    if repo.por_cpf(db, payload.cpf) or repo.por_email(db, payload.email):
        raise HTTPException(409, 'CPF ou e-mail já cadastrado.')
    try:
        usuario = Usuario(login=payload.login.lower(), senha_hash=hash_senha(payload.senha), perfil='aluno')
        db.add(usuario)
        db.flush()
        aluno = Aluno(
            id=usuario.id, nome=payload.nome, email=payload.email, cpf=payload.cpf,
            rg=payload.rg, endereco=payload.endereco, curso=payload.curso,
            instituicao_id=payload.instituicao_id,
        )
        db.add_all([aluno, Carteira(usuario_id=usuario.id, saldo=0)])
        db.commit()
        db.refresh(aluno)
        return aluno
    except IntegrityError as e:
        db.rollback()
        conflito(e)


def atualizar(db: Session, aluno: Aluno, payload: AlunoAtualizar):
    validar_instituicao(db, payload.instituicao_id)
    outro = repo.por_email(db, payload.email)
    if outro and outro.id != aluno.id:
        raise HTTPException(409, 'E-mail já cadastrado.')
    try:
        for campo in ('nome','email','rg','endereco','curso','instituicao_id'):
            setattr(aluno, campo, getattr(payload, campo))
        if payload.senha_nova:
            aluno.usuario.senha_hash = hash_senha(payload.senha_nova)
        db.commit()
        db.refresh(aluno)
        return aluno
    except IntegrityError as e:
        db.rollback()
        conflito(e)


def excluir(db: Session, aluno: Aluno):
    # Conservação de registros financeiros: contas com movimentação não são apagadas.
    from sqlalchemy import select, or_
    from app.models import TransacaoMoedas
    carteira = aluno.usuario.carteira
    if carteira:
        transacao = db.scalar(select(TransacaoMoedas.id).where(or_(
            TransacaoMoedas.origem_carteira_id == carteira.id,
            TransacaoMoedas.destino_carteira_id == carteira.id)).limit(1))
        if carteira.saldo != 0 or transacao:
            raise HTTPException(409, 'Cadastro com saldo ou movimentações não pode ser excluído. Solicite desativação administrativa.')
    existe_resgate = db.query(Resgate.id).filter(Resgate.aluno_id == aluno.id).first()
    if existe_resgate:
        raise HTTPException(409, 'Cadastro com resgates não pode ser excluído.')
    try:
        if carteira:
            db.delete(carteira)
        db.delete(aluno)
        db.delete(aluno.usuario)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(409, 'O cadastro possui vínculos e não pode ser excluído.') from e
