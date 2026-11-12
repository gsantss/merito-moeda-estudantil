"""Tarefas periódicas executadas dentro do próprio servidor da API.

No plano gratuito do Render não há agendador (cron) gratuito. Por isso, quando
TAREFAS_AUTOMATICAS=1 (padrão na nuvem), o servidor executa:

- o crédito semestral de 1.000 moedas, ao iniciar e a cada INTERVALO_CREDITO_SEGUNDOS.
  A operação é idempotente (uma vez por professor e semestre, garantido pelo banco);
- o envio da fila de e-mails, a cada INTERVALO_NOTIFICACOES_SEGUNDOS, se o SMTP estiver configurado.

Os scripts manuais (scripts/creditar_semestre.py e scripts/processar_notificacoes.py) continuam disponíveis.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from app.database import SessionLocal
from app.services import notificacoes
from app.services.financeiro import creditos_semestre

log = logging.getLogger('moeda.tarefas')

# Horário de Brasília (sem horário de verão desde 2019). Evita depender da base de fusos do sistema.
FUSO_BRASILIA = timezone(timedelta(hours=-3))


def semestre_atual(agora: datetime | None = None) -> str:
    """'AAAA/1' de janeiro a junho; 'AAAA/2' de julho a dezembro."""
    agora = agora or datetime.now(FUSO_BRASILIA)
    return f'{agora.year}/{1 if agora.month <= 6 else 2}'


def creditar_semestre_atual() -> dict:
    with SessionLocal() as db:
        return creditos_semestre(db, semestre_atual())


async def _executar(funcao, descricao: str):
    try:
        return await asyncio.to_thread(funcao)
    except Exception:
        log.exception('Falha na tarefa automática de %s.', descricao)
        return None


async def executar_periodicamente(parar: asyncio.Event, intervalo_notificacoes: int, intervalo_credito: int):
    loop = asyncio.get_running_loop()
    proximo_credito = 0.0
    if notificacoes.ConfigSmtp.do_ambiente() is None:
        log.info('SMTP não configurado: as notificações ficarão pendentes no banco.')
    while not parar.is_set():
        if loop.time() >= proximo_credito:
            resultado = await _executar(creditar_semestre_atual, 'crédito semestral')
            if resultado:
                log.info('Crédito semestral %s: %s professor(es) creditado(s), %s já creditado(s).',
                         resultado['semestre'], resultado['creditados'], resultado['ja_creditados'])
            proximo_credito = loop.time() + intervalo_credito
        resultado = await _executar(notificacoes.enviar_pendentes, 'envio de notificações')
        if resultado and resultado.get('tentadas'):
            log.info('Notificações: %s enviada(s) de %s tentada(s).', resultado['enviadas'], resultado['tentadas'])
        try:
            await asyncio.wait_for(parar.wait(), timeout=intervalo_notificacoes)
        except TimeoutError:
            pass
