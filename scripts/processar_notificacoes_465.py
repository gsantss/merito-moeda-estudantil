"""Despacha mensagens do outbox. SMTP configurável; sem SMTP não finge entrega."""
import os
import smtplib
import ssl
from email.message import EmailMessage
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Notificacao


def enviar_pendentes(limit=100):
    host = os.getenv('SMTP_HOST')
    if not host:
        print('SMTP_HOST não definido. Mensagens permanecerão pendentes no banco; configure SMTP antes de enviar.')
        return {'enviadas': 0, 'aviso': 'smtp_nao_configurado'}
    porta = int(os.getenv('SMTP_PORT', '587'))
    # SMTPS (porta 465) inicia o TLS desde a conexão; 587 utiliza STARTTLS.
    usar_ssl = os.getenv('SMTP_SSL', '1' if porta == 465 else '0') == '1'
    usuario = os.getenv('SMTP_USER', '')
    senha = os.getenv('SMTP_PASSWORD', '')
    remetente = os.getenv('SMTP_FROM', usuario)
    if not remetente:
        raise RuntimeError('Configure SMTP_FROM ou SMTP_USER.')
    enviados = 0
    with SessionLocal() as db:
        pendentes = db.scalars(select(Notificacao).where(Notificacao.status.in_(['pendente', 'falhou']),
                                                       Notificacao.tentativas < 5)
                               .order_by(Notificacao.criado_em).limit(limit)).all()
        for item in pendentes:
            msg = EmailMessage()
            msg['From'] = remetente; msg['To'] = item.destinatario
            msg['Subject'] = item.assunto; msg.set_content(item.corpo)
            try:
                if usar_ssl:
                    # Porta 465: SSL/TLS implícito; não executar starttls() novamente.
                    conexao = smtplib.SMTP_SSL(
                        host, porta, timeout=15, context=ssl.create_default_context()
                    )
                else:
                    # Porta 587: conectar em texto e negociar STARTTLS antes do login.
                    conexao = smtplib.SMTP(host, porta, timeout=15)
                with conexao as smtp:
                    if not usar_ssl and os.getenv('SMTP_STARTTLS', '1') == '1':
                        smtp.starttls(context=ssl.create_default_context())
                    if usuario:
                        smtp.login(usuario, senha)
                    smtp.send_message(msg)
                item.status = 'enviado'; enviados += 1
            except Exception as exc:
                item.status = 'falhou'
                print(f'Falha no envio da notificação {item.id}: {type(exc).__name__}: {exc}')
            finally:
                item.tentativas += 1
                db.commit()
    return {'enviadas': enviados, 'tentadas': len(pendentes)}

if __name__ == '__main__': print(enviar_pendentes())
