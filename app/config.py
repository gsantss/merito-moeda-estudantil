import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "moeda_estudantil.db"}')
SECRET_KEY = os.getenv('SECRET_KEY', 'CHAVE-DEMO-APENAS-LOCAL-ALTERE-EM-PRODUCAO-2026')
SESSION_HTTPS_ONLY = os.getenv('SESSION_HTTPS_ONLY', '0') == '1'
SEED_DEMO_PROFESSOR = os.getenv('SEED_DEMO_PROFESSOR', '1') == '1'

# LAB04S01 — tarefas automáticas dentro do servidor (app/tarefas.py):
# UC05 (crédito semestral, ator "agendador") e UC12 (envio da fila de e-mails).
TAREFAS_AUTOMATICAS = os.getenv('TAREFAS_AUTOMATICAS', '1') == '1'
INTERVALO_NOTIFICACOES_SEGUNDOS = int(os.getenv('INTERVALO_NOTIFICACOES_SEGUNDOS', '60'))
INTERVALO_CREDITO_SEGUNDOS = int(os.getenv('INTERVALO_CREDITO_SEGUNDOS', str(6 * 60 * 60)))
