"""LAB04S02: configuração de nuvem e separação frontend (Vercel) x backend (Render).

As tarefas automáticas (crédito semestral e fila de e-mails) são testadas em test_lab04s01.py."""
import json
import re
from pathlib import Path
import pytest
from app import config
from app.config import normalizar_url_banco
from app.main import app, resolver_pagina

RAIZ = Path(__file__).resolve().parent.parent
FRONTEND = RAIZ / 'frontend'
PAGINAS = sorted(FRONTEND.glob('*.html')) + sorted((FRONTEND / 'cadastro').glob('*.html'))


# ------------------------------------------------------------------ configuração
@pytest.mark.parametrize('entrada, esperado', [
    ('postgres://u:s@host:5432/db', 'postgresql+psycopg://u:s@host:5432/db'),
    ('postgresql://u:s@host/db', 'postgresql+psycopg://u:s@host/db'),
    ('postgresql+psycopg://u@h/db', 'postgresql+psycopg://u@h/db'),
    ('sqlite:///./moeda_estudantil.db', 'sqlite:///./moeda_estudantil.db'),
])
def test_url_do_banco_usa_driver_psycopg(entrada, esperado):
    assert normalizar_url_banco(entrada) == esperado


def _producao(monkeypatch, **valores):
    padrao = dict(EM_PRODUCAO=True, SECRET_KEY='k' * 64, DATABASE_URL='postgresql+psycopg://u@h/db',
                  SEED_DEMO_PROFESSOR=True, SEED_DEMO_COMPLETO=True, DEMO_SENHA='s' * 32, SESSION_HTTPS_ONLY=True)
    for nome, valor in {**padrao, **valores}.items():
        monkeypatch.setattr(config, nome, valor)


def test_producao_valida_com_segredos_proprios(monkeypatch):
    _producao(monkeypatch)
    config.validar_configuracao()


@pytest.mark.parametrize('ajuste, trecho', [
    ({'SECRET_KEY': config.CHAVE_DEMO}, 'SECRET_KEY'),
    ({'DEMO_SENHA': config.SENHA_DEMO_LOCAL}, 'DEMO_SENHA'),
    ({'DEMO_SENHA': None}, 'DEMO_SENHA'),
    ({'DATABASE_URL': 'sqlite:///x.db'}, 'SQLite'),
    ({'SESSION_HTTPS_ONLY': False}, 'SESSION_HTTPS_ONLY'),
])
def test_producao_recusa_segredos_de_demonstracao(monkeypatch, ajuste, trecho):
    _producao(monkeypatch, **ajuste)
    with pytest.raises(RuntimeError, match=trecho):
        config.validar_configuracao()


# ------------------------------------------------------------------ API
def test_saude_confirma_api_e_banco(ambiente):
    client, *_ = ambiente
    resposta = client.get('/api/saude')
    assert resposta.status_code == 200
    assert resposta.json()['status'] == 'ok'


def test_respostas_da_api_nao_sao_guardadas_em_cache(ambiente):
    client, *_ = ambiente
    assert client.get('/api/sessao').headers['cache-control'] == 'no-store'
    assert client.get('/api/instituicoes').headers['cache-control'] == 'no-store'
    assert 'cache-control' not in client.get('/login').headers


# ------------------------------------------------------------------ interface servida localmente
@pytest.mark.parametrize('url, pagina', [
    ('/', 'inicio'), ('/login', 'login'), ('/painel', 'painel'), ('/parceiros', 'parceiros'),
    ('/vantagens', 'vantagens'), ('/cadastro/aluno', 'cadastro-aluno'), ('/cadastro/empresa', 'cadastro-empresa'),
])
def test_paginas_com_urls_limpas_como_na_vercel(ambiente, url, pagina):
    client, *_ = ambiente
    resposta = client.get(url)
    assert resposta.status_code == 200
    assert f'data-page="{pagina}"' in resposta.text


def test_pagina_inexistente_e_tentativa_de_sair_da_pasta(ambiente):
    client, *_ = ambiente
    assert client.get('/nao-existe').status_code == 404
    assert resolver_pagina('../app/config') is None
    assert resolver_pagina('..%2F..%2Fetc/passwd') is None


def test_paginas_carregam_o_cliente_api_antes_das_telas():
    assert len(PAGINAS) == 7
    for pagina in PAGINAS:
        html = pagina.read_text(encoding='utf-8')
        scripts = re.findall(r'<script src="([^"]+)"', html)
        assert scripts == ['/static/js/cliente-api.js', '/static/js/app.js', '/static/js/sprint03.js'], pagina.name
        for recurso in re.findall(r'(?:src|href)="(/static/[^"]+)"', html):
            assert (FRONTEND / recurso.lstrip('/')).is_file(), f'{pagina.name}: {recurso} não existe'
        assert '{{' not in html and '{%' not in html, f'{pagina.name} ainda tem marcação Jinja'


def test_paginas_nao_usam_scripts_inline_bloqueados_pela_csp():
    arquivos = PAGINAS + sorted((FRONTEND / 'static' / 'js').glob('*.js'))
    for arquivo in arquivos:
        texto = arquivo.read_text(encoding='utf-8')
        assert not re.search(r'\son(error|load|click|submit)\s*=', texto), f'{arquivo.name} usa manipulador inline'
        assert not re.search(r'<script(?![^>]*\bsrc=)[^>]*>', texto), f'{arquivo.name} usa <script> inline'


# ------------------------------------------------------------------ alinhamento frontend x backend
def _caminhos_da_api():
    """Rotas publicadas pela API (esquema OpenAPI: independe de como os roteadores foram incluídos)."""
    return [c for c in app.openapi()['paths'] if c.startswith('/api/')]


def _rotas_da_api():
    return [re.compile('^' + re.sub(r'\{[^}]+\}', '[^/]+', c) + '$') for c in _caminhos_da_api()]


def _caminhos_usados_no_frontend():
    caminhos = set()
    for js in (FRONTEND / 'static' / 'js').glob('*.js'):
        texto = js.read_text(encoding='utf-8')
        for literal in re.findall(r"['`](/api/[^'`]*)['`]", texto):
            literal = re.sub(r'\$\{[^}]+\}', 'X', literal)
            if literal == '/api/':
                continue  # prefixo montado dinamicamente ('/api/' + endpoint), coberto pelas rotas abaixo
            caminhos.add(literal + 'X' if literal.endswith('/') else literal)
    return caminhos


def test_todo_caminho_da_api_usado_pela_interface_existe_no_backend():
    rotas = _rotas_da_api()
    caminhos = _caminhos_usados_no_frontend()
    assert len(caminhos) >= 15
    inexistentes = sorted(c for c in caminhos if not any(r.match(c) for r in rotas))
    assert inexistentes == [], f'A interface chama rotas que não existem na API: {inexistentes}'


def test_vercel_repassa_api_para_o_servico_do_render():
    vercel = json.loads((FRONTEND / 'vercel.json').read_text(encoding='utf-8'))
    render = (RAIZ / 'render.yaml').read_text(encoding='utf-8')
    servico = re.search(r'-\s*type:\s*web\s*\n\s*name:\s*(\S+)', render).group(1)
    regra = next(r for r in vercel['rewrites'] if r['source'].startswith('/api/'))
    assert regra['destination'].startswith(f'https://{servico}.onrender.com/api/'), \
        'O destino do proxy na Vercel deve ser a URL do serviço definido em render.yaml'
    assert vercel['cleanUrls'] is True


def test_render_usa_rotas_e_variaveis_que_existem():
    render = (RAIZ / 'render.yaml').read_text(encoding='utf-8')
    saude = re.search(r'healthCheckPath:\s*(\S+)', render).group(1)
    assert saude in _caminhos_da_api()
    assert 'app.main:app' in render
    codigo = '\n'.join(p.read_text(encoding='utf-8') for p in (RAIZ / 'app').rglob('*.py'))
    for variavel in re.findall(r'-\s*key:\s*(\w+)', render):
        assert variavel in codigo, f'render.yaml define {variavel}, mas o código não a usa'
