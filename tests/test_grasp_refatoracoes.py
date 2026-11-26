"""Testes unitários e de regressão para as 3 refatorações GRASP (LAB04S03)."""
from datetime import datetime, timezone
import pytest
from fastapi import HTTPException
from sqlalchemy import select
from app.models import Carteira, Cupom, Notificacao, Professor, TransacaoMoedas, Usuario, Vantagem, agora
from app.repositories import vantagens as vantagens_repo
from app.schemas import AlunoCriar, EmpresaCriar
from app.schemas_extra import VantagemCriar
from app.services import alunos as alunos_service
from app.services import auth as auth_service
from app.services import empresas as empresas_service
from app.services import financeiro as financeiro_service
from app.services import notificacoes as notificacoes_service
from app.services import vantagens as vantagens_service

FOTO = 'https://images.example.org/item.jpg'


def _criar_empresa(db, login: str = 'empresa.grasp', email: str = 'contato@grasp.local'):
    return empresas_service.criar(
        db,
        EmpresaCriar(
            nome='Parceiro GRASP',
            email_contato=email,
            cnpj=None,
            descricao='Parceiro para testes GRASP.',
            login=login,
            senha='Segura@123',
        ),
    )


def _criar_aluno(db, inst_id: str, login: str = 'aluno.grasp', email: str = 'aluno@grasp.local'):
    return alunos_service.criar(
        db,
        AlunoCriar(
            nome='Estudante GRASP',
            email=email,
            cpf='52998224725',
            rg='MG999999',
            endereco='Rua da Arquitetura, 100',
            curso='Engenharia de Software',
            instituicao_id=inst_id,
            login=login,
            senha='Segura@123',
        ),
    )


# ------------------------------------------------------------------ Refatoração 1: Vantagens (Service + Repository)
def test_vantagens_service_e_repository_fluxo_e_posse(ambiente):
    _, _, _, Session = ambiente
    with Session() as db:
        e1 = _criar_empresa(db, 'emp1', 'emp1@grasp.local')
        e2 = _criar_empresa(db, 'emp2', 'emp2@grasp.local')
        criada = vantagens_service.criar(
            db,
            e1,
            VantagemCriar(
                titulo='Desconto Livraria',
                descricao='Vale desconto de 20% em livros técnicos.',
                foto_url=FOTO,
                custo=120,
            ),
        )
        assert criada['empresa'] == 'Parceiro GRASP'
        assert vantagens_repo.existe_por_empresa(db, e1.id) is True
        assert vantagens_repo.existe_por_empresa(db, e2.id) is False
        assert len(vantagens_service.listar_ativas(db)) == 1
        assert len(vantagens_service.listar_da_empresa(db, e1.id)) == 1

        with pytest.raises(HTTPException) as exc_404:
            vantagens_service.atualizar(
                db,
                e1,
                '00000000-0000-0000-0000-000000000000',
                VantagemCriar(titulo='Inexistente', descricao='Descrição válida.', foto_url=FOTO, custo=10),
            )
        assert exc_404.value.status_code == 404

        with pytest.raises(HTTPException) as exc_403:
            vantagens_service.desativar(db, e2.id, criada['id'])
        assert exc_403.value.status_code == 403

        desativada = vantagens_service.desativar(db, e1.id, criada['id'])
        assert 'desativada' in desativada['mensagem'].lower()
        assert vantagens_service.listar_ativas(db) == []


# ------------------------------------------------------------------ Refatoração 2: Creator (Notificações) + Expert (Cupom/Transacao)
def test_cupom_e_transacao_information_expert():
    cupom = Cupom.criar_para_resgate('resgate-1')
    assert cupom.codigo.startswith('MER-')
    assert len(cupom.codigo) == 20
    assert cupom.foi_utilizado is False
    cupom.utilizado_em = agora()
    assert cupom.foi_utilizado is True

    tx = TransacaoMoedas(
        id='tx-1',
        tipo='distribuicao',
        quantidade=50,
        origem_carteira_id='carteira-prof',
        destino_carteira_id='carteira-aluno',
        motivo='Ótima apresentação',
        semestre=None,
        data_hora=datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc),
    )
    assert tx.direcao_para('carteira-prof') == 'saida'
    assert tx.direcao_para('carteira-aluno') == 'entrada'
    item = tx.para_extrato('carteira-aluno')
    assert item['direcao'] == 'entrada'
    assert item['quantidade'] == 50
    assert item['motivo'] == 'Ótima apresentação'


def test_notificacoes_creator_sem_commit_prematuro_e_saldo_atualizado(ambiente):
    _, inst_id, _, Session = ambiente
    with Session() as db:
        prof = db.scalar(select(Professor))
        aluno = _criar_aluno(db, inst_id)
        empresa = _criar_empresa(db)
        vantagem = Vantagem(
            empresa_id=empresa.id,
            titulo='Café Especial',
            descricao='Café expresso gratuito no campus.',
            foto_url=FOTO,
            custo=80,
            ativa=True,
        )
        db.add(vantagem)
        db.commit()

        # Enfileiramento não realiza commit próprio: rollback desfaz a notificação junto com a transação.
        notificacoes_service.enfileirar_recebimento_moedas(
            db,
            email_aluno=aluno.email,
            nome_professor=prof.nome,
            quantidade=10,
            motivo='Teste rollback',
            transacao_id=None,
        )
        db.rollback()
        assert db.query(Notificacao).count() == 0

        financeiro_service.creditos_semestre(db, '2026/2')
        dist = financeiro_service.distribuir(db, prof.id, aluno.id, 200, 'Participação exemplar')
        assert dist['saldo_atual'] == 800

        resg = financeiro_service.resgatar(db, aluno.id, vantagem.id)
        assert resg['saldo_atual'] == 120
        assert resg['cupom'].startswith('MER-')
        assert db.query(Notificacao).count() == 3


# ------------------------------------------------------------------ Refatoração 3: Auth, Contas e Usuario Information Expert
def test_usuario_information_expert_e_auth_service(ambiente):
    _, inst_id, _, Session = ambiente
    with Session() as db:
        prof_usuario = db.scalar(select(Usuario).where(Usuario.perfil == 'professor'))
        assert prof_usuario.nome_exibicao == 'Professor Teste'
        assert prof_usuario.possui_carteira() is True

        aluno = _criar_aluno(db, inst_id)
        assert aluno.usuario.nome_exibicao == 'Estudante GRASP'
        assert aluno.usuario.possui_carteira() is True

        empresa = _criar_empresa(db)
        assert empresa.usuario.nome_exibicao == 'Parceiro GRASP'
        assert empresa.usuario.possui_carteira() is False

        autenticado = auth_service.autenticar(db, '  ALUNO.GRASP ', 'Segura@123')
        assert autenticado.id == aluno.id
        assert auth_service.obter_usuario_ativo(db, autenticado.id).id == aluno.id

        with pytest.raises(HTTPException) as exc_401:
            auth_service.autenticar(db, 'aluno.grasp', 'senha-errada')
        assert exc_401.value.status_code == 401


def test_desativacao_empresa_e_aluno_via_services(ambiente):
    _, inst_id, _, Session = ambiente
    with Session() as db:
        empresa = _criar_empresa(db)
        vantagem = vantagens_service.criar(
            db,
            empresa,
            VantagemCriar(
                titulo='Combo Lanche',
                descricao='Combo completo na cantina universitária.',
                foto_url=FOTO,
                custo=150,
            ),
        )
        empresas_service.desativar(db, empresa.usuario)
        db.refresh(empresa.usuario)
        assert empresa.usuario.ativo is False
        assert auth_service.obter_usuario_ativo(db, empresa.id) is None
        assert db.get(Vantagem, vantagem['id']).ativa is False

        aluno = _criar_aluno(db, inst_id)
        alunos_service.desativar(db, aluno.usuario)
        db.refresh(aluno.usuario)
        assert aluno.usuario.ativo is False
        assert db.scalar(select(Carteira).where(Carteira.usuario_id == aluno.id)) is not None
