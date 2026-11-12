"""Envio da fila de notificações (outbox) por e-mail.

As transações gravam as notificações como 'pendente' junto com a operação financeira
(app/services/financeiro.py). Este módulo as entrega depois, fora do caminho crítico.

Indireção e Variações Protegidas (GRASP): o processamento da fila depende só da
interface EnviadorEmail. O SMTP é uma implementação trocável, por exemplo por uma API
HTTP de e-mail, sem alterar as regras de negócio.
"""
import logging
import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Notificacao

log = logging.getLogger('moeda.notificacoes')

MAX_TENTATIVAS = 5


class EnviadorEmail(Protocol):
    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None: ...


@dataclass(frozen=True)
class ConfigSmtp:
    host: str
    porta: int
    usuario: str
    senha: str
    remetente: str
    usar_ssl: bool
    usar_starttls: bool

    @classmethod
    def do_ambiente(cls) -> 'ConfigSmtp | None':
        """Lê SMTP_* do ambiente. Sem SMTP_HOST, devolve None (as mensagens ficam pendentes)."""
        host = os.getenv('SMTP_HOST', '').strip()
        if not host:
            return None
        porta = int(os.getenv('SMTP_PORT', '587'))
        usuario = os.getenv('SMTP_USER', '').strip()
        remetente = os.getenv('SMTP_FROM', '').strip() or usuario
        if not remetente:
            raise RuntimeError('Configure SMTP_FROM ou SMTP_USER.')
        # Porta 465: TLS desde a conexão (SMTPS). Demais portas (587, 2525): STARTTLS.
        usar_ssl = os.getenv('SMTP_SSL', '1' if porta == 465 else '0').strip() == '1'
        usar_starttls = not usar_ssl and os.getenv('SMTP_STARTTLS', '1').strip() == '1'
        return cls(host, porta, usuario, os.getenv('SMTP_PASSWORD', ''), remetente, usar_ssl, usar_starttls)


class EnviadorSmtp:
    """Implementação de EnviadorEmail via SMTP (STARTTLS ou SSL)."""

    def __init__(self, config: ConfigSmtp, timeout: int = 15):
        self.config = config
        self.timeout = timeout

    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
        c = self.config
        msg = EmailMessage()
        msg['From'] = c.remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.set_content(corpo)
        contexto = ssl.create_default_context()
        if c.usar_ssl:
            conexao = smtplib.SMTP_SSL(c.host, c.porta, timeout=self.timeout, context=contexto)
        else:
            conexao = smtplib.SMTP(c.host, c.porta, timeout=self.timeout)
        with conexao as smtp:
            if c.usar_starttls:
                smtp.starttls(context=contexto)
            if c.usuario:
                smtp.login(c.usuario, c.senha)
            smtp.send_message(msg)


def processar_pendentes(db: Session, enviador: EnviadorEmail, limite: int = 100) -> dict:
    """Tenta enviar as notificações pendentes ou com falha (até MAX_TENTATIVAS por mensagem)."""
    pendentes = db.scalars(
        select(Notificacao)
        .where(Notificacao.status.in_(['pendente', 'falhou']), Notificacao.tentativas < MAX_TENTATIVAS)
        .order_by(Notificacao.criado_em)
        .limit(limite)
    ).all()
    enviadas = 0
    for item in pendentes:
        try:
            enviador.enviar(item.destinatario, item.assunto, item.corpo)
            item.status = 'enviado'
            enviadas += 1
        except Exception as exc:  # falha de rede ou recusa do servidor: tenta de novo no próximo ciclo
            item.status = 'falhou'
            log.warning('Falha no envio da notificação %s: %s: %s', item.id, type(exc).__name__, str(exc)[:200])
        finally:
            item.tentativas += 1
            db.commit()
    return {'enviadas': enviadas, 'tentadas': len(pendentes)}


def enviar_pendentes(limite: int = 100) -> dict:
    """Ponto de entrada usado pelo script manual e pela tarefa automática."""
    from app.database import SessionLocal  # import tardio: permite testar sem banco configurado

    config = ConfigSmtp.do_ambiente()
    if config is None:
        return {'enviadas': 0, 'aviso': 'smtp_nao_configurado'}
    with SessionLocal() as db:
        return processar_pendentes(db, EnviadorSmtp(config), limite)
