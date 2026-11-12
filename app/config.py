import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "moeda_estudantil.db"}')
SECRET_KEY = os.getenv('SECRET_KEY', 'CHAVE-DEMO-APENAS-LOCAL-ALTERE-EM-PRODUCAO-2026')
SESSION_HTTPS_ONLY = os.getenv('SESSION_HTTPS_ONLY', '0') == '1'
SEED_DEMO_PROFESSOR = os.getenv('SEED_DEMO_PROFESSOR', '1') == '1'
