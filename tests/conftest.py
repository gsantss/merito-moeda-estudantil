import os

# Os testes nunca usam o banco de desenvolvimento: a aplicação sobe com um SQLite
# em memória descartável, e cada teste recebe um banco próprio (fixture "ambiente").
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['AMBIENTE'] = 'local'
os.environ['TAREFAS_AUTOMATICAS'] = '0'

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import normalizar_url_banco
from app.main import app
from app.database import Base, get_db
from app.models import Instituicao, Professor, Usuario, Carteira
from app.security import hash_senha

# Opcional: TEST_DATABASE_URL=postgresql://... roda a suíte contra o PostgreSQL (mesmo banco da nuvem).
# ATENÇÃO: todas as tabelas desse banco são apagadas e recriadas a cada teste.
URL_TESTE = os.getenv('TEST_DATABASE_URL')


def criar_engine_teste():
    if URL_TESTE:
        engine = create_engine(normalizar_url_banco(URL_TESTE))
        Base.metadata.drop_all(bind=engine)
        return engine
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    @event.listens_for(engine, 'connect')
    def pragma(dbapi_conn, conn_record):
        dbapi_conn.execute('PRAGMA foreign_keys=ON')
    return engine


@pytest.fixture
def ambiente():
    engine = criar_engine_teste()
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(engine, expire_on_commit=False)
    with Session() as db:
        i = Instituicao(nome='PUC Minas Teste')
        outra = Instituicao(nome='Outra instituição')
        db.add_all([i, outra]); db.flush()
        professor = Usuario(login='prof@demo.local', senha_hash=hash_senha('Demo@12345'), perfil='professor')
        db.add(professor); db.flush()
        db.add_all([Professor(id=professor.id, nome='Professor Teste', cpf='12345678909',
                              departamento='Tecnologia', instituicao_id=i.id), Carteira(usuario_id=professor.id)])
        db.commit()
        id_inst, id_outra = i.id, outra.id
    def get_test_db():
        with Session() as db:
            yield db
    app.dependency_overrides[get_db] = get_test_db
    try:
        with TestClient(app) as client:
            yield client, id_inst, id_outra, Session
    finally:
        app.dependency_overrides.clear()
        if URL_TESTE:
            Base.metadata.drop_all(bind=engine)
        engine.dispose()

@pytest.fixture
def aluno_payload(ambiente):
    _, inst, _, _ = ambiente
    return dict(nome='Maria Silva', email='maria@example.com', cpf='52998224725',
                rg='MG123456', endereco='Rua das Flores, 10', curso='Engenharia de Software',
                instituicao_id=inst, login='maria', senha='Segura@123')

@pytest.fixture
def empresa_payload():
    return dict(nome='Restaurante Campus', email_contato='contato@campus.com', cnpj=None,
                descricao='Descontos para estudantes.', login='campus', senha='Segura@123')


def headers(client):
    return {'X-CSRF-Token': client.get('/api/sessao').json()['csrf_token']}


def login(client, usuario, senha):
    return client.post('/api/auth/login', json={'login': usuario, 'senha': senha}, headers=headers(client))
