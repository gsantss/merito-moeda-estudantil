"""Despacha manualmente as mensagens da fila (outbox). SMTP configurável; sem SMTP não finge entrega.

Na nuvem, a própria API faz isso periodicamente (TAREFAS_AUTOMATICAS=1). Lógica em app/services/notificacoes.py.
Porta 465 usa SSL; 587 (ou 2525) usa STARTTLS. Veja SMTP_* no .env.example.
"""
from app.services.notificacoes import enviar_pendentes


def main():
    resultado = enviar_pendentes()
    if resultado.get('aviso') == 'smtp_nao_configurado':
        print('SMTP_HOST não definido. Mensagens permanecerão pendentes no banco; configure SMTP antes de enviar.')
    print(resultado)

if __name__ == '__main__': main()
