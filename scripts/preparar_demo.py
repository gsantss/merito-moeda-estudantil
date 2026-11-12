"""Popula dados fictícios para apresentação. Idempotente; não apaga informações existentes."""
from sqlalchemy import select
from app.database import Base, engine, SessionLocal
from app.models import Usuario, Instituicao, Vantagem
from app.schemas import AlunoCriar, EmpresaCriar
from app.services.alunos import criar as criar_aluno
from app.services.empresas import criar as criar_empresa
from app.services.financeiro import creditos_semestre
from app.seed import popular_banco


def main():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        popular_banco(db)
        inst = db.scalar(select(Instituicao).where(Instituicao.nome == 'PUC Minas'))
        if not db.scalar(select(Usuario).where(Usuario.login == 'aluno.demo')):
            criar_aluno(db, AlunoCriar(nome='Estudante Exemplo', email='estudante@demo.local',
                        cpf='52998224725', rg='MG-123456', endereco='Belo Horizonte, MG',
                        curso='Engenharia de Software', instituicao_id=inst.id,
                        login='aluno.demo', senha='Demo@12345'))
        if not db.scalar(select(Usuario).where(Usuario.login == 'empresa.demo')):
            criar_empresa(db, EmpresaCriar(nome='Lanchonete Acadêmica (Demonstração)',
                          email_contato='parceiro@demo.local', cnpj=None,
                          descricao='Exemplo de empresa do laboratório.',
                          login='empresa.demo', senha='Demo@12345'))
        empresa = db.scalar(select(Usuario).where(Usuario.login == 'empresa.demo')).empresa
        if not db.scalar(select(Vantagem).where(Vantagem.empresa_id == empresa.id)):
            db.add(Vantagem(empresa_id=empresa.id, titulo='Desconto no lanche',
                            descricao='Cupom fictício de desconto em um lanche do campus.',
                            foto_url='https://images.unsplash.com/photo-1568901346375-23c9450c58cd',
                            custo=150, ativa=True))
            db.commit()
        status=creditos_semestre(db,'2026/2')
        print('Demo preparada:',status)
        print('Professor: professor@demo.local / Demo@12345')
        print('Aluno: aluno.demo / Demo@12345')
        print('Empresa: empresa.demo / Demo@12345')
        print('ATENÇÃO: dados e senhas fictícios para ambiente local. Não use publicamente.')

if __name__ == '__main__': main()
