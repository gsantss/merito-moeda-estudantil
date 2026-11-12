from tests.conftest import headers, login
from sqlalchemy import select
from app.models import Usuario, Aluno, EmpresaParceira, Carteira


def test_inicio_e_instituicoes(ambiente):
    c, inst, _, _ = ambiente
    assert c.get('/').status_code == 200
    assert 'Mérito' in c.get('/').text
    assert any(x['id'] == inst for x in c.get('/api/instituicoes').json())
    assert c.get('/docs').status_code == 200


def test_aluno_criar_ler_editar_excluir(ambiente, aluno_payload):
    c, _, _, Session = ambiente
    assert c.get('/api/alunos').status_code == 401
    assert c.post('/api/alunos', json=aluno_payload).status_code == 403  # Anti-CSRF
    criado = c.post('/api/alunos', json=aluno_payload, headers=headers(c))
    assert criado.status_code == 201, criado.text
    uid = criado.json()['aluno']['id']
    assert 'senha' not in str(criado.json()).lower()
    assert c.post('/api/alunos', json=aluno_payload, headers=headers(c)).status_code == 409
    with Session() as db:
        assert db.get(Aluno, uid) is not None
        assert db.scalar(select(Carteira).where(Carteira.usuario_id == uid)).saldo == 0
        assert db.get(Usuario, uid).senha_hash != aluno_payload['senha']
    assert login(c, 'maria', 'senha-errada').status_code == 401
    assert login(c, 'maria', 'Segura@123').status_code == 200
    assert c.get('/api/alunos/' + uid).json()['email'] == aluno_payload['email']
    update = {k: aluno_payload[k] for k in ('nome','email','rg','endereco','curso','instituicao_id')}
    update['curso'] = 'Ciência da Computação'
    update['senha_nova'] = 'SenhaNova@45'
    alterado = c.put('/api/alunos/' + uid, json=update, headers=headers(c))
    assert alterado.status_code == 200, alterado.text
    assert alterado.json()['aluno']['curso'] == 'Ciência da Computação'
    assert c.get('/api/alunos').json()[0]['nome'] == aluno_payload['nome']
    assert c.delete('/api/alunos/' + uid, headers=headers(c)).status_code == 200
    assert c.get('/api/alunos/' + uid).status_code == 401
    with Session() as db:
        assert db.get(Usuario, uid) is None
        assert db.get(Aluno, uid) is None
    assert login(c, 'maria','SenhaNova@45').status_code == 401


def test_empresa_criar_ler_editar_excluir(ambiente, empresa_payload):
    c, _, _, Session = ambiente
    r = c.post('/api/empresas', json=empresa_payload, headers=headers(c))
    assert r.status_code == 201, r.text
    uid = r.json()['empresa']['id']
    assert c.post('/api/empresas', json=empresa_payload, headers=headers(c)).status_code == 409
    empresas = c.get('/api/empresas').json()
    assert any(e['id'] == uid for e in empresas)
    assert 'email_contato' not in empresas[0]  # Consulta pública não divulga o email
    assert 'email_contato' not in c.get('/api/empresas/' + uid).json()
    with Session() as db:
        assert db.get(EmpresaParceira, uid).nome == empresa_payload['nome']
    assert login(c,'campus','Segura@123').status_code == 200
    assert c.get('/api/empresas/' + uid).json()['email_contato'] == empresa_payload['email_contato']
    alteracao = {k: empresa_payload[k] for k in ('nome','email_contato','cnpj','descricao')}
    alteracao['nome'] = 'Novo Restaurante'
    alteracao['senha_nova'] = None
    r = c.put('/api/empresas/' + uid, json=alteracao, headers=headers(c))
    assert r.status_code == 200, r.text
    assert r.json()['empresa']['nome'] == 'Novo Restaurante'
    assert c.delete('/api/empresas/' + uid, headers=headers(c)).status_code == 200
    assert c.get('/api/empresas/' + uid).status_code == 404


def test_perfis_nao_alteram_contas_alheias(ambiente, aluno_payload, empresa_payload):
    c, inst, outro_inst, _ = ambiente
    r = c.post('/api/alunos', json=aluno_payload, headers=headers(c))
    aluno_id = r.json()['aluno']['id']
    r = c.post('/api/empresas', json=empresa_payload, headers=headers(c))
    empresa_id = r.json()['empresa']['id']
    assert login(c,'maria','Segura@123').status_code == 200
    payload_empresa = {k: empresa_payload[k] for k in ('nome','email_contato','cnpj','descricao')}
    assert c.put('/api/empresas/' + empresa_id, json=payload_empresa, headers=headers(c)).status_code == 403
    assert c.delete('/api/empresas/' + empresa_id, headers=headers(c)).status_code == 403
    assert login(c,'campus','Segura@123').status_code == 200
    payload_aluno = {k: aluno_payload[k] for k in ('nome','email','rg','endereco','curso','instituicao_id')}
    assert c.put('/api/alunos/' + aluno_id, json=payload_aluno, headers=headers(c)).status_code == 403
    assert c.get('/api/alunos/' + aluno_id).status_code == 403
    assert login(c,'prof@demo.local','Demo@12345').status_code == 200
    vistos = c.get('/api/alunos').json()
    assert any(a['id'] == aluno_id for a in vistos)
    assert 'cpf' not in vistos[0]
    assert c.delete('/api/alunos/' + aluno_id, headers=headers(c)).status_code == 403
    payload_aluno['instituicao_id'] = 'inexistente'
    assert c.put('/api/alunos/' + aluno_id, json=payload_aluno, headers=headers(c)).status_code == 403


def test_regras_e_validacoes(ambiente, aluno_payload, empresa_payload):
    c, _, _, _ = ambiente
    invalido = dict(aluno_payload, instituicao_id='nao-existe')
    assert c.post('/api/alunos',json=invalido,headers=headers(c)).status_code == 422
    invalido = dict(aluno_payload, cpf='123')
    assert c.post('/api/alunos',json=invalido,headers=headers(c)).status_code == 422
    invalido = dict(empresa_payload, cnpj='123')
    assert c.post('/api/empresas',json=invalido,headers=headers(c)).status_code == 422
    criado = c.post('/api/empresas',json=empresa_payload,headers=headers(c))
    assert criado.status_code == 201
    outro = dict(aluno_payload, login='campus')
    assert c.post('/api/alunos',json=outro,headers=headers(c)).status_code == 409


def test_professor_ve_apenas_alunos_da_propria_instituicao(ambiente, aluno_payload):
    c, _, inst2, _ = ambiente
    c.post('/api/alunos',json=aluno_payload,headers=headers(c))
    fora = dict(aluno_payload, cpf='11144477735', email='outra@example.com',
                login='outro', instituicao_id=inst2, nome='Outro aluno')
    assert c.post('/api/alunos',json=fora,headers=headers(c)).status_code == 201
    assert login(c,'prof@demo.local','Demo@12345').status_code == 200
    alunos = c.get('/api/alunos').json()
    assert len(alunos) == 1
    assert alunos[0]['nome'] == 'Maria Silva'
