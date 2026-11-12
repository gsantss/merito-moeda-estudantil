"""LAB04S01: os diagramas de sequência e de visão geral de interação correspondem ao código.

Se algum teste falhar depois de uma mudança no código, atualize o diagrama (ou o código) para que voltem
a coincidir: o alinhamento entre modelo e código faz parte da avaliação do projeto.
"""
import re
from pathlib import Path
import pytest
from app.main import app

RAIZ = Path(__file__).resolve().parent.parent
PASTA_SD = RAIZ / 'docs' / 'diagramas' / 'sequencia'
DIAGRAMAS = sorted(PASTA_SD.glob('sd*.puml'))
VISAO_GERAL = RAIZ / 'docs' / 'diagramas' / 'visao_geral_interacao.puml'

PARTICIPANTE = re.compile(r'^(?:actor|boundary|control|entity|participant|database|collections|queue)\s+"([^"]*)"\s+as\s+(\w+)', re.M)
MENSAGEM = re.compile(r'^\s*(\w+)\s*->\s*(\w+)\s*:\s*(.+)$', re.M)   # só chamadas (->), não respostas (-->)
HTTP = re.compile(r'^(GET|POST|PUT|PATCH|DELETE)\s+(/api/[\w/{}-]*)')
CHAMADA = re.compile(r'^([A-Za-z_]\w*)\(')


def _arquivos_dos_participantes(texto):
    arquivos = {}
    for rotulo, apelido in PARTICIPANTE.findall(texto):
        caminho = re.search(r'\((app/[\w/]+\.py)\)', rotulo.replace('\\n', ' '))
        if caminho:
            arquivos[apelido] = caminho.group(1)
    return arquivos


def _rotas_da_api():
    rotas = set()
    for caminho, operacoes in app.openapi()['paths'].items():
        padrao = re.compile('^' + re.sub(r'\{[^}]+\}', '[^/]+', caminho) + '$')
        rotas.update((metodo.upper(), padrao) for metodo in operacoes)
    return rotas


def test_existe_um_diagrama_de_sequencia_por_caso_de_uso():
    assert len(DIAGRAMAS) == 10
    titulos = ' '.join(re.search(r'^title (.+)$', d.read_text(encoding='utf-8'), re.M).group(1) for d in DIAGRAMAS)
    for caso in ['UC01', 'UC02', 'UC03', 'UC04', 'UC05', 'UC06', 'UC07', 'UC08', 'UC09', 'UC10', 'UC11', 'UC12', 'UC13']:
        assert caso in titulos, f'{caso} não aparece em nenhum diagrama de sequência'


@pytest.mark.parametrize('diagrama', DIAGRAMAS, ids=lambda d: d.stem)
def test_participantes_e_chamadas_existem_no_codigo(diagrama):
    texto = diagrama.read_text(encoding='utf-8')
    arquivos = _arquivos_dos_participantes(texto)
    assert arquivos, 'o diagrama deve indicar o arquivo de código de cada participante'
    for caminho in set(arquivos.values()):
        assert (RAIZ / caminho).is_file(), f'{caminho} não existe'
    rotas = _rotas_da_api()
    verificadas = 0
    for _, destino, rotulo in MENSAGEM.findall(texto):
        rotulo = rotulo.strip()
        http = HTTP.match(rotulo)
        if http:
            metodo, caminho = http.groups()
            assert any(m == metodo and p.match(caminho) for m, p in rotas), f'rota {metodo} {caminho} não existe na API'
            verificadas += 1
            continue
        chamada = CHAMADA.match(rotulo)
        if chamada and destino in arquivos:
            nome = chamada.group(1)
            codigo = (RAIZ / arquivos[destino]).read_text(encoding='utf-8')
            assert re.search(rf'\b(def|class)\s+{nome}\b', codigo), f'{nome}() não existe em {arquivos[destino]}'
            verificadas += 1
    assert verificadas >= 2


def test_visao_geral_referencia_todos_os_diagramas_de_sequencia():
    texto = VISAO_GERAL.read_text(encoding='utf-8')
    referenciados = set(re.findall(r'(SD\d{2}) —', texto))
    existentes = {d.stem[:4].upper() for d in DIAGRAMAS}
    assert referenciados == existentes
