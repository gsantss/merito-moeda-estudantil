"""Popula dados fictícios para apresentação. Idempotente; não apaga informações existentes.

Na nuvem, o mesmo resultado é obtido com SEED_DEMO_COMPLETO=1 (feito ao iniciar a API).
"""
from app.config import DEMO_SENHA, EM_PRODUCAO
from app.database import Base, engine, SessionLocal
from app.seed import popular_demo_completo
from app.services.financeiro import creditos_semestre
from app.tarefas import semestre_atual


def main():
    if not DEMO_SENHA:
        raise SystemExit('Defina DEMO_SENHA com a senha das contas de demonstração.')
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        popular_demo_completo(db, DEMO_SENHA)
        status = creditos_semestre(db, semestre_atual())
    print('Demo preparada:', status)
    senha = '<valor de DEMO_SENHA>' if EM_PRODUCAO else DEMO_SENHA
    print(f'Professor: professor@demo.local / {senha}')
    print(f'Aluno: aluno.demo / {senha}')
    print(f'Empresa: empresa.demo / {senha}')
    print('ATENÇÃO: dados fictícios. A senha local padrão serve apenas para uso na sua máquina.')

if __name__ == '__main__': main()
