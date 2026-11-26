"""Serviços de domínio transacionais - RN03 a RN11.

Transação de banco envolve saldo, extrato e outbox. Nenhuma chamada SMTP ocorre
no caminho crítico da operação. Débitos são UPDATEs condicionais (saldo >= custo),
com rollback de todos os lançamentos em caso de erro.
"""
import re
from sqlalchemy import select, update, or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import (Aluno, Carteira, CreditoSemestral, Cupom, EmpresaParceira,
                        Professor, Resgate, TransacaoMoedas, Vantagem, agora)
from app.services import notificacoes


def carteira_usuario(db: Session, usuario_id: str) -> Carteira:
    c = db.scalar(select(Carteira).where(Carteira.usuario_id == usuario_id))
    if not c:
        raise HTTPException(404, 'Carteira não encontrada.')
    return c


def _debitar(db: Session, carteira: Carteira, quantidade: int):
    result = db.execute(update(Carteira).where(Carteira.id == carteira.id, Carteira.saldo >= quantidade)
                        .values(saldo=Carteira.saldo - quantidade))
    if result.rowcount != 1:
        raise HTTPException(409, 'Saldo insuficiente para esta operação.')


def _creditar(db: Session, carteira: Carteira, quantidade: int):
    db.execute(update(Carteira).where(Carteira.id == carteira.id)
               .values(saldo=Carteira.saldo + quantidade))


def extrato(db: Session, usuario_id: str):
    carteira = carteira_usuario(db, usuario_id)
    registros = db.scalars(select(TransacaoMoedas).where(or_(
        TransacaoMoedas.origem_carteira_id == carteira.id,
        TransacaoMoedas.destino_carteira_id == carteira.id,
    )).order_by(TransacaoMoedas.data_hora.desc(), TransacaoMoedas.id.desc())).all()
    return {'saldo': carteira.saldo, 'movimentacoes': [t.para_extrato(carteira.id) for t in registros]}


def creditos_semestre(db: Session, semestre: str):
    """Uso por operador local agendado. Uma execução repetida não concede créditos extras."""
    if not re.fullmatch(r'\d{4}/[12]', semestre):
        raise ValueError('Semestre inválido: informe AAAA/1 ou AAAA/2.')
    professores = db.scalars(select(Professor).join(Professor.usuario).where(
        Professor.usuario.has(ativo=True)).order_by(Professor.id)).all()
    contabilizados = ignorados = 0
    for p in professores:
        if db.scalar(select(CreditoSemestral.id).where(
            CreditoSemestral.professor_id == p.id, CreditoSemestral.semestre == semestre)):
            ignorados += 1
            continue
        c = carteira_usuario(db, p.id)
        t = TransacaoMoedas(tipo='credito_semestral', quantidade=1000,
                            destino_carteira_id=c.id, semestre=semestre,
                            motivo='Crédito automático do semestre ' + semestre)
        try:
            # SAVEPOINT mantém intacta a sessão ao encontrar crédito idempotente.
            with db.begin_nested():
                db.add(t)
                db.flush()
                db.add(CreditoSemestral(professor_id=p.id, semestre=semestre, transacao_id=t.id))
                db.flush()
                _creditar(db, c, 1000)
            db.commit()
            contabilizados += 1
        except IntegrityError:
            db.rollback()
            ignorados += 1
    return {'semestre': semestre, 'creditados': contabilizados, 'ja_creditados': ignorados}


def distribuir(db: Session, professor_id: str, aluno_id: str, quantidade: int, motivo: str):
    motivo = motivo.strip()
    if not motivo or quantidade < 1:
        raise HTTPException(422, 'Informe quantidade positiva e motivo obrigatório.')
    professor = db.get(Professor, professor_id)
    aluno = db.get(Aluno, aluno_id)
    if not professor or not aluno:
        raise HTTPException(404, 'Professor ou aluno não encontrado.')
    if professor.instituicao_id != aluno.instituicao_id:
        raise HTTPException(403, 'Você só pode premiar alunos de sua instituição.')
    origem, destino = carteira_usuario(db, professor_id), carteira_usuario(db, aluno_id)
    try:
        _debitar(db, origem, quantidade)
        _creditar(db, destino, quantidade)
        t = TransacaoMoedas(tipo='distribuicao', quantidade=quantidade,
                            origem_carteira_id=origem.id, destino_carteira_id=destino.id, motivo=motivo)
        db.add(t)
        db.flush()
        notificacoes.enfileirar_recebimento_moedas(
            db,
            email_aluno=aluno.email,
            nome_professor=professor.nome,
            quantidade=quantidade,
            motivo=motivo,
            transacao_id=t.id,
        )
        db.commit()
        db.refresh(origem)
        return {'transacao_id': t.id, 'quantidade': quantidade, 'saldo_atual': origem.saldo}
    except Exception:
        db.rollback()
        raise


def resgatar(db: Session, aluno_id: str, vantagem_id: str):
    aluno = db.get(Aluno, aluno_id)
    v = db.get(Vantagem, vantagem_id)
    if not aluno or not v or not v.ativa:
        raise HTTPException(404, 'Vantagem indisponível.')
    empresa = db.get(EmpresaParceira, v.empresa_id)
    c = carteira_usuario(db, aluno_id)
    try:
        _debitar(db, c, v.custo)
        t = TransacaoMoedas(tipo='resgate', quantidade=v.custo, origem_carteira_id=c.id,
                            motivo='Resgate: ' + v.titulo)
        db.add(t)
        db.flush()
        r = Resgate(aluno_id=aluno_id, vantagem_id=v.id,
                    transacao_id=t.id, custo_aplicado=v.custo)
        db.add(r)
        db.flush()
        cupom = Cupom.criar_para_resgate(r.id)
        db.add(cupom)
        db.flush()
        notificacoes.enfileirar_resgate_cupom(
            db,
            email_aluno=aluno.email,
            email_empresa=empresa.email_contato,
            titulo_vantagem=v.titulo,
            custo=v.custo,
            codigo_cupom=cupom.codigo,
            transacao_id=t.id,
            cupom_id=cupom.id,
        )
        db.commit()
        db.refresh(c)
        return {'resgate_id': r.id, 'cupom': cupom.codigo,
                'vantagem': v.titulo, 'custo': v.custo, 'saldo_atual': c.saldo,
                'notificacoes': 'enfileiradas'}
    except Exception:
        db.rollback()
        raise


def listar_cupons(db: Session, aluno_id: str):
    rows = db.execute(select(Cupom, Resgate, Vantagem).join(Resgate, Cupom.resgate_id == Resgate.id)
                      .join(Vantagem, Resgate.vantagem_id == Vantagem.id)
                      .where(Resgate.aluno_id == aluno_id).order_by(Cupom.emitido_em.desc())).all()
    return [{'codigo': cupom.codigo, 'vantagem': v.titulo,
             'emitido_em': cupom.emitido_em.isoformat(),
             'utilizado_em': cupom.utilizado_em.isoformat() if cupom.utilizado_em else None}
            for cupom, _, v in rows]


def validar_cupom(db: Session, empresa_id: str, codigo: str, consumir: bool = False):
    item = db.execute(select(Cupom, Resgate, Vantagem).join(Resgate, Cupom.resgate_id == Resgate.id)
                      .join(Vantagem, Resgate.vantagem_id == Vantagem.id).where(Cupom.codigo == codigo)).first()
    if not item or item[2].empresa_id != empresa_id:
        raise HTTPException(404, 'Cupom não encontrado para sua empresa.')
    cupom, resgate, v = item
    if consumir:
        status = db.execute(update(Cupom).where(Cupom.id == cupom.id, Cupom.utilizado_em.is_(None))
                            .values(utilizado_em=agora()))
        if status.rowcount != 1:
            raise HTTPException(409, 'Este cupom já foi utilizado.')
        db.commit()
        db.refresh(cupom)
    return {'codigo': cupom.codigo, 'vantagem': v.titulo, 'resgate_id': resgate.id,
            'utilizado': cupom.foi_utilizado}
