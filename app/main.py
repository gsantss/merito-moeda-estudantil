from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app import models  # registra tabelas no metadata
from app.config import SECRET_KEY, SESSION_HTTPS_ONLY
from app.database import Base, engine, SessionLocal
from app.routers import auth, alunos, empresas, consulta, financeiro, pages
from app.seed import popular_banco

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        popular_banco(db)
    yield

app = FastAPI(title='Sistema de Moeda Estudantil — LAB03S03', version='3.0.0', lifespan=lifespan,
              description='Sprint 03: CRUDs finais, distribuição, crédito semestral, vantagens, resgates e cupons.')
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie='moeda_session',
                   same_site='lax', https_only=SESSION_HTTPS_ONLY, max_age=60 * 60 * 8)
app.mount('/static', StaticFiles(directory=str(Path(__file__).resolve().parent / 'static')), name='static')
for router in (auth.router, alunos.router, empresas.router, consulta.router, financeiro.router, pages.router):
    app.include_router(router)
