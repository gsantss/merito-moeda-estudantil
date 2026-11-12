"""LAB04S01: casos de uso restantes — UC05 (crédito semestral pelo agendador) e UC12 (envio de e-mails)."""
import asyncio
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app import config, tarefas
from app.main import app
from app.models import Carteira, CreditoSemestral, Notificacao, Professor
from app.services import notificacoes
from app.services.notificacoes import MAX_TENTATIVAS, ConfigSmtp, processar_pendentes
from app.tarefas import semestre_atual


# ------------------------------------------------------------------ UC05: crédito semestral automático
@pytest.mark.parametrize('data, esperado', [
    (datetime(2026, 1, 1), '2026/1'), (datetime(2026, 6, 30), '2026/1'),
    (datetime(2026, 7, 1), '2026/2'), (datetime(2026, 12, 31), '2026/2'),
])
def test_semestre_atual(data, esperado):
    assert semestre_atual(data) == esperado


def test_agendador_credita_o_semestre_atual_uma_unica_vez(ambiente, monkeypatch):
    _, _, _, Session = ambiente
    monkeypatch.setattr(tarefas, 'SessionLocal', Session)
    primeira = tarefas.creditar_semestre_atual()
    segunda = tarefas.creditar_semestre_atual()
    assert (primeira['creditados'], segunda['creditados'], segunda['ja_creditados']) == (1, 0, 1)
    with Session() as db:
        professor = db.scalar(select(Professor))
        saldo = db.scalar(select(Carteira.saldo).where(Carteira.usuario_id == professor.id))
        semestres = db.scalars(select(CreditoSemestral.semestre)).all()
    assert saldo == 1000
    assert semestres == [semestre_atual()]


def test_ciclo_automatico_executa_credito_e_envio_e_para_sob_demanda(monkeypatch):
    chamadas = []
    monkeypatch.setattr(tarefas, 'creditar_semestre_atual',
                        lambda: chamadas.append('credito') or {'semestre': '2026/2', 'creditados': 0, 'ja_creditados': 1})
    monkeypatch.setattr(notificacoes, 'enviar_pendentes', lambda: chamadas.append('envio') or {'enviadas': 0, 'tentadas': 0})

    async def rodar():
        parar = asyncio.Event()
        ciclo = asyncio.create_task(tarefas.executar_periodicamente(parar, intervalo_notificacoes=0.05, intervalo_credito=3600))
        await asyncio.sleep(0.2)
        parar.set()
        await asyncio.wait_for(ciclo, timeout=2)

    asyncio.run(rodar())
    assert chamadas[:2] == ['credito', 'envio']
    assert chamadas.count('credito') == 1        # crédito: ao iniciar e depois a cada intervalo_credito
    assert chamadas.count('envio') >= 2           # fila de e-mails: a cada intervalo_notificacoes


def test_falha_em_uma_tarefa_nao_derruba_o_ciclo(monkeypatch):
    chamadas = []
    def falhar():
        chamadas.append('credito')
        raise RuntimeError('banco indisponível')
    monkeypatch.setattr(tarefas, 'creditar_semestre_atual', falhar)
    monkeypatch.setattr(notificacoes, 'enviar_pendentes', lambda: chamadas.append('envio') or {})

    async def rodar():
        parar = asyncio.Event()
        ciclo = asyncio.create_task(tarefas.executar_periodicamente(parar, 0.05, 3600))
        await asyncio.sleep(0.15)
        parar.set()
        await asyncio.wait_for(ciclo, timeout=2)

    asyncio.run(rodar())
    assert 'envio' in chamadas


def test_servidor_inicia_e_encerra_as_tarefas_automaticas(monkeypatch):
    eventos = []
    async def ciclo_falso(parar, intervalo_notificacoes, intervalo_credito):
        eventos.append('iniciou')
        await parar.wait()
        eventos.append('encerrou')
    monkeypatch.setattr(config, 'TAREFAS_AUTOMATICAS', True)
    monkeypatch.setattr(tarefas, 'executar_periodicamente', ciclo_falso)
    with TestClient(app):
        pass
    assert eventos == ['iniciou', 'encerrou']


# ------------------------------------------------------------------ UC12: envio das notificações por e-mail
@pytest.mark.parametrize('porta, ssl_esperado, starttls_esperado', [(465, True, False), (587, False, True), (2525, False, True)])
def test_smtp_escolhe_ssl_ou_starttls_pela_porta(monkeypatch, porta, ssl_esperado, starttls_esperado):
    monkeypatch.setenv('SMTP_HOST', 'smtp.exemplo.com')
    monkeypatch.setenv('SMTP_PORT', str(porta))
    monkeypatch.setenv('SMTP_USER', 'conta@exemplo.com')
    for variavel in ('SMTP_SSL', 'SMTP_STARTTLS', 'SMTP_FROM'):
        monkeypatch.delenv(variavel, raising=False)
    cfg = ConfigSmtp.do_ambiente()
    assert (cfg.usar_ssl, cfg.usar_starttls, cfg.remetente) == (ssl_esperado, starttls_esperado, 'conta@exemplo.com')


def test_sem_smtp_as_notificacoes_ficam_pendentes(monkeypatch):
    monkeypatch.delenv('SMTP_HOST', raising=False)
    assert ConfigSmtp.do_ambiente() is None
    assert notificacoes.enviar_pendentes() == {'enviadas': 0, 'aviso': 'smtp_nao_configurado'}


class EnviadorFalso:
    def __init__(self, falhar_para=()):
        self.enviados, self.falhar_para = [], set(falhar_para)

    def enviar(self, destinatario, assunto, corpo):
        if destinatario in self.falhar_para:
            raise ConnectionError('servidor recusou')
        self.enviados.append(destinatario)


def test_fila_de_notificacoes_envia_e_repete_falhas_ate_o_limite(ambiente):
    _, _, _, Session = ambiente
    with Session() as db:
        db.add_all([Notificacao(destinatario='ok@exemplo.com', assunto='a', corpo='b'),
                    Notificacao(destinatario='falha@exemplo.com', assunto='a', corpo='b')])
        db.commit()
        enviador = EnviadorFalso(falhar_para={'falha@exemplo.com'})
        assert processar_pendentes(db, enviador) == {'enviadas': 1, 'tentadas': 2}
        for _ in range(MAX_TENTATIVAS + 2):
            processar_pendentes(db, enviador)
        status = {n.destinatario: (n.status, n.tentativas) for n in db.query(Notificacao).all()}
    assert enviador.enviados == ['ok@exemplo.com']
    assert status == {'ok@exemplo.com': ('enviado', 1), 'falha@exemplo.com': ('falhou', MAX_TENTATIVAS)}
