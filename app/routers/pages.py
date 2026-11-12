from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / 'templates'))

@router.get('/')
def inicio(request: Request):
    return templates.TemplateResponse(request, 'inicio.html', {'pagina': 'inicio', 'titulo': 'Início'})

@router.get('/cadastro/aluno')
def cadastro_aluno(request: Request):
    return templates.TemplateResponse(request, 'cadastro_aluno.html', {'pagina': 'cadastro-aluno', 'titulo': 'Cadastrar aluno'})

@router.get('/cadastro/empresa')
def cadastro_empresa(request: Request):
    return templates.TemplateResponse(request, 'cadastro_empresa.html', {'pagina': 'cadastro-empresa', 'titulo': 'Cadastrar empresa'})

@router.get('/login')
def pagina_login(request: Request):
    return templates.TemplateResponse(request, 'login.html', {'pagina': 'login', 'titulo': 'Entrar'})

@router.get('/painel')
def painel(request: Request):
    return templates.TemplateResponse(request, 'painel.html', {'pagina': 'painel', 'titulo': 'Meu painel'})

@router.get('/parceiros')
def parceiros(request: Request):
    return templates.TemplateResponse(request, 'parceiros.html', {'pagina': 'parceiros', 'titulo': 'Empresas parceiras'})

@router.get('/vantagens')
def catalogo(request: Request):
    return templates.TemplateResponse(request, 'vantagens.html', {'pagina': 'vantagens', 'titulo': 'Catálogo de vantagens'})
