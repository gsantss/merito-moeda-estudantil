import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app import models  # registra tabelas no metadata
from app import config, tarefas
from app.config import SECRET_KEY, SESSION_HTTPS_ONLY
from app.database import Base, engine, SessionLocal
from app.routers import auth, alunos, empresas, consulta, financeiro, pages
from app.seed import popular_banco

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(name)s: %(message)s')

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        popular_banco(db)
    # LAB04S01: crédito semestral (UC05) e envio da fila de e-mails (UC12) sem operador.
    parar = asyncio.Event()
    tarefa = None
    if config.TAREFAS_AUTOMATICAS:
        tarefa = asyncio.create_task(tarefas.executar_periodicamente(
            parar, config.INTERVALO_NOTIFICACOES_SEGUNDOS, config.INTERVALO_CREDITO_SEGUNDOS))
    yield
    parar.set()
    if tarefa:
        await tarefa

app = FastAPI(title='Sistema de Moeda Estudantil — LAB04', version='4.1.0', lifespan=lifespan,
              description='CRUDs, distribuição, crédito semestral automático, vantagens, resgates, cupons e envio de e-mails.')
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie='moeda_session',
                   same_site='lax', https_only=SESSION_HTTPS_ONLY, max_age=60 * 60 * 8)
app.mount('/static', StaticFiles(directory=str(Path(__file__).resolve().parent / 'static')), name='static')
for router in (auth.router, alunos.router, empresas.router, consulta.router, financeiro.router, pages.router):
    app.include_router(router)
