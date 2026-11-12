"""Configuração por variáveis de ambiente.

Localmente, os valores vêm do arquivo .env (veja .env.example). Na nuvem (Render),
vêm das variáveis do serviço, definidas em render.yaml. Com AMBIENTE=producao, a
aplicação se recusa a iniciar com chaves ou senhas de demonstração.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

CHAVE_DEMO = 'CHAVE-DEMO-APENAS-LOCAL-ALTERE-EM-PRODUCAO-2026'
SENHA_DEMO_LOCAL = 'Demo@12345'


def _flag(nome: str, padrao: bool) -> bool:
    return os.getenv(nome, '1' if padrao else '0').strip() == '1'


def normalizar_url_banco(url: str) -> str:
    """Converte a URL do PostgreSQL (ex.: a fornecida pelo Render) para o driver psycopg 3.

    'postgres://...' e 'postgresql://...' -> 'postgresql+psycopg://...'. Outras URLs ficam iguais.
    """
    for prefixo in ('postgres://', 'postgresql://'):
        if url.startswith(prefixo):
            return 'postgresql+psycopg://' + url[len(prefixo):]
    return url


# 'local' (padrão) ou 'producao' (nuvem).
AMBIENTE = os.getenv('AMBIENTE', 'local').strip().lower()
EM_PRODUCAO = AMBIENTE == 'producao'

DATABASE_URL = normalizar_url_banco(os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "moeda_estudantil.db"}'))
SECRET_KEY = os.getenv('SECRET_KEY', CHAVE_DEMO)
# Cookie de sessão só trafega em HTTPS. Na nuvem é sempre HTTPS.
SESSION_HTTPS_ONLY = _flag('SESSION_HTTPS_ONLY', EM_PRODUCAO)

# Professor de demonstração (professores não se cadastram sozinhos: são pré-cadastrados).
SEED_DEMO_PROFESSOR = _flag('SEED_DEMO_PROFESSOR', True)
# Também cria aluno, empresa e uma vantagem de demonstração (útil para a avaliação na nuvem).
SEED_DEMO_COMPLETO = _flag('SEED_DEMO_COMPLETO', False)
# Senha das contas de demonstração. Na nuvem é obrigatória e gerada pelo Render (nunca a senha local).
DEMO_SENHA = os.getenv('DEMO_SENHA') or (None if EM_PRODUCAO else SENHA_DEMO_LOCAL)

# LAB04S01 — tarefas automáticas dentro do servidor (app/tarefas.py):
# UC05 (crédito semestral, ator "agendador") e UC12 (envio da fila de e-mails).
TAREFAS_AUTOMATICAS = _flag('TAREFAS_AUTOMATICAS', True)
INTERVALO_NOTIFICACOES_SEGUNDOS = int(os.getenv('INTERVALO_NOTIFICACOES_SEGUNDOS', '60'))
INTERVALO_CREDITO_SEGUNDOS = int(os.getenv('INTERVALO_CREDITO_SEGUNDOS', str(6 * 60 * 60)))

# O próprio FastAPI serve as páginas da pasta frontend/ (uso local). Na nuvem, quem serve é a Vercel.
FRONTEND_DIR = BASE_DIR / 'frontend'
SERVIR_FRONTEND = _flag('SERVIR_FRONTEND', not EM_PRODUCAO)


def validar_configuracao() -> None:
    """Impede que a aplicação suba na nuvem com segredos de demonstração."""
    if not EM_PRODUCAO:
        return
    problemas = []
    if SECRET_KEY == CHAVE_DEMO or len(SECRET_KEY) < 32:
        problemas.append('SECRET_KEY ausente, curta ou igual à chave de demonstração')
    if DATABASE_URL.startswith('sqlite'):
        problemas.append('DATABASE_URL aponta para SQLite; na nuvem use PostgreSQL (o disco do servidor é apagado a cada reinício)')
    if (SEED_DEMO_PROFESSOR or SEED_DEMO_COMPLETO) and (not DEMO_SENHA or DEMO_SENHA == SENHA_DEMO_LOCAL or len(DEMO_SENHA) < 12):
        problemas.append('DEMO_SENHA ausente, curta ou igual à senha local de demonstração')
    if not SESSION_HTTPS_ONLY:
        problemas.append('SESSION_HTTPS_ONLY deve ser 1')
    if problemas:
        raise RuntimeError('Configuração inválida para produção: ' + '; '.join(problemas) + '.')
