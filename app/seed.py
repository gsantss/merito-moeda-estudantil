"""Pré-cadastro idempotente: instituições, professor de demonstração e, opcionalmente, demo completa.

A senha das contas de demonstração vem de DEMO_SENHA (app/config.py). Localmente o padrão é
'Demo@12345'; na nuvem a senha é gerada pelo Render e nunca fica no código.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Instituicao, Usuario, Professor, Carteira, Vantagem
from app.security import hash_senha
from app.config import SEED_DEMO_PROFESSOR, DEMO_SENHA

INSTITUICOES = (
    'PUC Minas',
    'Instituição Parceira Exemplo',
)

def popular_banco(db: Session):
    for nome in INSTITUICOES:
        if not db.scalar(select(Instituicao).where(Instituicao.nome == nome)):
            db.add(Instituicao(nome=nome))
    db.commit()
    if not SEED_DEMO_PROFESSOR:
        return
    if db.scalar(select(Usuario).where(Usuario.login == 'professor@demo.local')):
        return
    puc = db.scalar(select(Instituicao).where(Instituicao.nome == 'PUC Minas'))
    usuario = Usuario(login='professor@demo.local', senha_hash=hash_senha(DEMO_SENHA), perfil='professor')
    db.add(usuario)
    db.flush()
    db.add_all([
        Professor(id=usuario.id, nome='Professor Demonstração', cpf='00000000000',
                  departamento='Engenharia de Software', instituicao_id=puc.id),
        Carteira(usuario_id=usuario.id, saldo=0),
    ])
    db.commit()


def popular_demo_completo(db: Session, senha: str):
    """Aluno, empresa e vantagem fictícios. Idempotente: não altera o que já existe."""
    from app.schemas import AlunoCriar, EmpresaCriar
    from app.services.alunos import criar as criar_aluno
    from app.services.empresas import criar as criar_empresa

    popular_banco(db)
    inst = db.scalar(select(Instituicao).where(Instituicao.nome == 'PUC Minas'))
    if not db.scalar(select(Usuario).where(Usuario.login == 'aluno.demo')):
        criar_aluno(db, AlunoCriar(nome='Estudante Exemplo', email='estudante@demo.local',
                    cpf='52998224725', rg='MG-123456', endereco='Belo Horizonte, MG',
                    curso='Engenharia de Software', instituicao_id=inst.id,
                    login='aluno.demo', senha=senha))
    if not db.scalar(select(Usuario).where(Usuario.login == 'empresa.demo')):
        criar_empresa(db, EmpresaCriar(nome='Lanchonete Acadêmica (Demonstração)',
                      email_contato='parceiro@demo.local', cnpj=None,
                      descricao='Exemplo de empresa do laboratório.',
                      login='empresa.demo', senha=senha))
    empresa = db.scalar(select(Usuario).where(Usuario.login == 'empresa.demo')).empresa
    if not db.scalar(select(Vantagem).where(Vantagem.empresa_id == empresa.id)):
        db.add(Vantagem(empresa_id=empresa.id, titulo='Desconto no lanche',
                        descricao='Cupom fictício de desconto em um lanche do campus.',
                        foto_url='https://images.unsplash.com/photo-1568901346375-23c9450c58cd',
                        custo=150, ativa=True))
        db.commit()
