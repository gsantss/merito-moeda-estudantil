import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from app import models  # noqa: F401  registra tabelas no metadata
from app import config, tarefas
from app.database import Base, engine, SessionLocal, get_db
from app.routers import auth, alunos, empresas, consulta, financeiro
from app.seed import popular_banco, popular_demo_completo

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(name)s: %(message)s')


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.validar_configuracao()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        popular_banco(db)
        if config.SEED_DEMO_COMPLETO:
            popular_demo_completo(db, config.DEMO_SENHA)
    parar = asyncio.Event()
    tarefa = None
    if config.TAREFAS_AUTOMATICAS:
        tarefa = asyncio.create_task(tarefas.executar_periodicamente(
            parar, config.INTERVALO_NOTIFICACOES_SEGUNDOS, config.INTERVALO_CREDITO_SEGUNDOS))
    yield
    parar.set()
    if tarefa:
        await tarefa


app = FastAPI(title='Sistema de Moeda Estudantil — LAB04', version='4.2.0', lifespan=lifespan,
              description='API do Mérito+: cadastros, autenticação, distribuição de moedas, crédito semestral, '
                          'vantagens, resgates e cupons. Na nuvem, a interface (Vercel) acessa esta API pelo caminho /api.')
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY, session_cookie='moeda_session',
                   same_site='lax', https_only=config.SESSION_HTTPS_ONLY, max_age=60 * 60 * 8)


@app.middleware('http')
async def sem_cache_na_api(request: Request, call_next):
    """Respostas da API dependem do usuário logado: nenhum proxy ou CDN pode guardá-las."""
    resposta = await call_next(request)
    if request.url.path.startswith('/api/'):
        resposta.headers['Cache-Control'] = 'no-store'
    return resposta


for router in (auth.router, alunos.router, empresas.router, consulta.router, financeiro.router):
    app.include_router(router)


@app.get('/api/saude', tags=['Infraestrutura'])
def saude(db: Session = Depends(get_db)):
    """Verificação de saúde usada pelo Render: confirma que a API responde e o banco está acessível."""
    db.execute(text('SELECT 1'))
    return {'status': 'ok', 'ambiente': config.AMBIENTE}


# ---------------------------------------------------------------- Interface (View)
# Na nuvem, as páginas de frontend/ são publicadas pela Vercel. Localmente (SERVIR_FRONTEND=1),
# o próprio FastAPI as serve, com as mesmas URLs "limpas" da Vercel (/login -> login.html).

def resolver_pagina(caminho: str) -> Path | None:
    raiz = config.FRONTEND_DIR.resolve()
    caminho = caminho.strip('/')
    candidatos = [raiz / 'index.html'] if not caminho else [raiz / f'{caminho}.html', raiz / caminho / 'index.html']
    for arquivo in candidatos:
        arquivo = arquivo.resolve()
        if arquivo.is_file() and raiz in arquivo.parents:
            return arquivo
    return None


if config.SERVIR_FRONTEND and config.FRONTEND_DIR.is_dir():
    app.mount('/static', StaticFiles(directory=str(config.FRONTEND_DIR / 'static')), name='static')

    @app.get('/{caminho:path}', include_in_schema=False)
    def pagina(caminho: str):
        arquivo = resolver_pagina(caminho)
        if arquivo is None:
            raise HTTPException(404, 'Página não encontrada.')
        return FileResponse(arquivo)
else:
    @app.get('/', include_in_schema=False)
    def raiz():
        return {'servico': 'API do Sistema de Moeda Estudantil (Mérito+)',
                'documentacao': '/docs', 'saude': '/api/saude'}
