"""Cobertura de negócios, isolamento entre perfis, idempotência e atomicidade."""
import pytest
from sqlalchemy import select
from app.models import (Usuario, Carteira, Vantagem, Resgate, Cupom, TransacaoMoedas,
                        CreditoSemestral, Notificacao)
from app.services.financeiro import creditos_semestre
from tests.conftest import login, headers

FOTO = 'https://images.example.org/sanduiche.jpg'

def criar_aluno(c, payload):
    r = c.post('/api/alunos', json=payload, headers=headers(c))
    assert r.status_code == 201, r.text
    return r.json()['aluno']['id']

def criar_empresa(c, payload):
    r = c.post('/api/empresas', json=payload, headers=headers(c))
    assert r.status_code == 201, r.text
    return r.json()['empresa']['id']

def vantagem(c, custo=200):
    r = c.post('/api/vantagens', json={
        'titulo':'Lanche universitário', 'descricao':'Um sanduíche completo',
        'foto_url':FOTO, 'custo':custo},headers=headers(c))
    assert r.status_code == 201, r.text
    return r.json()['id']

def test_credito_semestral_idempotente_e_acumulativo(ambiente):
    c, _, _, Sess = ambiente
    with Sess() as db:
        u=db.scalar(select(Usuario).where(Usuario.login=='prof@demo.local'))
        resp=creditos_semestre(db, '2026/2')
        assert resp['creditados']==1
        resp=creditos_semestre(db, '2026/2')
        assert resp['ja_creditados']==1
        assert db.scalar(select(Carteira).where(Carteira.usuario_id==u.id)).saldo==1000
        assert db.query(CreditoSemestral).count()==1
        assert creditos_semestre(db, '2027/1')['creditados']==1
        assert db.scalar(select(Carteira).where(Carteira.usuario_id==u.id)).saldo==2000
        with pytest.raises(ValueError): creditos_semestre(db, '2026/3')

def test_transferencia_integral_restricoes_e_notificacao(ambiente, aluno_payload):
    c,_,outra,Sess=ambiente
    aid=criar_aluno(c,aluno_payload)
    fora=dict(aluno_payload,login='fora',email='fora@example.com',cpf='11144477735',instituicao_id=outra)
    aid_fora=criar_aluno(c,fora)
    assert login(c,'prof@demo.local','Demo@12345').status_code==200
    with Sess() as db: creditos_semestre(db,'2026/2')
    def enviar(id, q, motivo):
        return c.post('/api/distribuicoes',json={'aluno_id':id,'quantidade':q,'motivo':motivo},headers=headers(c))
    assert enviar(aid,1200,'Excelente participação').status_code==409
    assert enviar(aid_fora,50,'Boa participação').status_code==403
    assert enviar(aid,50,'  ').status_code==422
    assert enviar(aid,-5,'teste').status_code==422
    assert enviar(aid,175,'Participação na apresentação').status_code==201
    saldo=c.get('/api/extrato').json()
    assert saldo['saldo']==825
    assert len(saldo['movimentacoes'])==2
    with Sess() as db:
        assert db.scalar(select(Carteira).where(Carteira.usuario_id==aid)).saldo==175
        assert db.query(TransacaoMoedas).filter_by(tipo='distribuicao').count()==1
        assert db.query(Notificacao).count()==1
        assert db.query(Notificacao).one().status=='pendente'
    assert login(c, 'maria','Segura@123').status_code==200
    assert c.get('/api/extrato').json()['movimentacoes'][0]['direcao']=='entrada'
    assert enviar(aid,5,'Alteração indevida').status_code==403

def test_vantagens_resgates_cupom_unico_empresa_e_saldo(ambiente,aluno_payload,empresa_payload):
    c,_,_,Sess=ambiente
    aid=criar_aluno(c,aluno_payload)
    eid=criar_empresa(c,empresa_payload)
    assert login(c,'campus','Segura@123').status_code==200
    vid=vantagem(c,100)
    assert len(c.get('/api/vantagens/minhas').json())==1
    assert login(c,'maria','Segura@123').status_code==200
    assert c.post('/api/resgates',json={'vantagem_id':vid},headers=headers(c)).status_code==409
    with Sess() as db:
        from app.services.financeiro import carteira_usuario
        carteira_usuario(db,aid).saldo=250
        db.commit()
    r=c.post('/api/resgates',json={'vantagem_id':vid},headers=headers(c))
    assert r.status_code==201,r.text
    data=r.json(); assert data['saldo_atual']==150
    assert data['cupom'].startswith('MER-')
    assert len(c.get('/api/cupons').json())==1
    with Sess() as db:
        assert db.query(Resgate).count()==1
        assert db.query(Cupom).count()==1
        assert db.query(Notificacao).count()==2
        assert db.query(TransacaoMoedas).filter_by(tipo='resgate').count()==1
    assert login(c,'campus','Segura@123').status_code==200
    assert c.get('/api/cupons/conferir/'+data['cupom']).status_code==200
    assert c.post('/api/cupons/utilizar',json={'codigo':data['cupom']},headers=headers(c)).status_code==200
    assert c.post('/api/cupons/utilizar',json={'codigo':data['cupom']},headers=headers(c)).status_code==409
    with Sess() as db:assert db.query(Cupom).one().utilizado_em is not None
    assert c.delete('/api/vantagens/'+vid,headers=headers(c)).status_code==200
    assert not c.get('/api/vantagens').json()
    assert len(c.get('/api/vantagens/minhas').json())==1
    assert c.delete('/api/empresas/'+eid,headers=headers(c)).status_code==409
    assert c.patch('/api/empresas/'+eid+'/desativar',headers=headers(c)).status_code==200
    assert login(c,'campus','Segura@123').status_code==401

def test_segurança_cruzada_e_edicao_vantagem(ambiente,aluno_payload,empresa_payload):
    c,_,_,_=ambiente
    aid=criar_aluno(c,aluno_payload)
    criar_empresa(c,empresa_payload)
    assert c.post('/api/vantagens',json={'titulo':'Teste', 'descricao':'Descrição válida', 'foto_url':FOTO, 'custo':1},headers=headers(c)).status_code==401
    assert login(c,'campus','Segura@123').status_code==200
    vid=vantagem(c)
    payload={'titulo':'Novo benefício','descricao':'Nova descrição completa','foto_url':FOTO,'custo':50,'ativa':False}
    assert c.put('/api/vantagens/'+vid,json=payload,headers=headers(c)).status_code==200
    assert not c.get('/api/vantagens').json()
    assert login(c,'maria','Segura@123').status_code==200
    assert c.put('/api/vantagens/'+vid,json=payload,headers=headers(c)).status_code==403
    assert c.delete('/api/vantagens/'+vid,headers=headers(c)).status_code==403
    assert c.get('/api/vantagens/minhas').status_code==403
    assert c.get('/api/cupons/conferir/MER-12345678').status_code==403
    assert c.patch('/api/alunos/'+aid+'/desativar',headers=headers(c)).status_code==200
    assert login(c,'maria','Segura@123').status_code==401

def test_emails_pendentes_sem_smtp_nao_sao_enviados(ambiente,monkeypatch):
    monkeypatch.delenv('SMTP_HOST', raising=False)
    from scripts.processar_notificacoes import enviar_pendentes
    assert enviar_pendentes()['enviadas']==0
