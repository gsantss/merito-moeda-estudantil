"""Gera relatório acadêmico PDF da LAB03S02 alinhado visualmente com LAB03S01."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, PageBreak, Paragraph,
    Spacer, Table, TableStyle, NextPageTemplate, KeepTogether, Image, CondPageBreak, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'docs'/'LAB03S02_Relatorio_Completo.pdf'
NAVY=colors.HexColor('#18354E'); TEAL=colors.HexColor('#078C88')
PALE=colors.HexColor('#F1F6F8'); GOLD=colors.HexColor('#D19A43')
GREY=colors.HexColor('#667984'); BORDER=colors.HexColor('#D6E0E5')
PAGE_W,PAGE_H=A4

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if not Path(FONT).exists():
    FONT='/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
    FONT_B='/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('BodyLab',FONT))
pdfmetrics.registerFont(TTFont('BodyLabBold',FONT_B))

styles={
 't':ParagraphStyle('body',fontName='BodyLab',fontSize=9.1,leading=15,textColor=NAVY,spaceAfter=10),
 'h1':ParagraphStyle('h1',fontName='BodyLabBold',fontSize=17,leading=24,textColor=NAVY,spaceBefore=5,spaceAfter=15),
 'h2':ParagraphStyle('h2',fontName='BodyLabBold',fontSize=11.5,leading=17,textColor=NAVY,spaceBefore=14,spaceAfter=9),
 'h3':ParagraphStyle('h3',fontName='BodyLabBold',fontSize=9.5,leading=15,textColor=TEAL,spaceBefore=12,spaceAfter=6),
 'caption':ParagraphStyle('caption',fontName='BodyLab',fontSize=7.9,leading=12,textColor=GREY,spaceAfter=9),
 'small':ParagraphStyle('small',fontName='BodyLab',fontSize=7.6,leading=12,textColor=NAVY),
 'smallwhite':ParagraphStyle('smallwhite',fontName='BodyLabBold',fontSize=8,leading=12,textColor=colors.white),
 'title':ParagraphStyle('title',fontName='BodyLabBold',fontSize=30,leading=39,textColor=NAVY),
 'cover':ParagraphStyle('cover',fontName='BodyLabBold',fontSize=16,leading=25,textColor=TEAL),
 'overline':ParagraphStyle('overline',fontName='BodyLabBold',fontSize=9,leading=16,textColor=GREY),
}

def P(txt,style='t'): return Paragraph(txt,styles[style])
def escape_cell(t): return escape(str(t))
def bullet(t): return P('<font color="#078C88"><b>•</b></font>  '+t,'t')

def sec(n,titulo): return P(f'{n}. {titulo}','h1')

def tbl(rows,widths=None,header=True):
    data=[]
    for rix,row in enumerate(rows):
        data.append([P(escape_cell(v),'smallwhite' if header and rix==0 else 'small') for v in row])
    table=Table(data,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),
      ('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),
      ('BOTTOMPADDING',(0,0),(-1,-1),9),('GRID',(0,0),(-1,-1),.4,BORDER)]
    if header:
        cmds += [('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE])]
    else:
        cmds += [('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.white,PALE])]
    table.setStyle(TableStyle(cmds))
    return table

def page_decor(canvas,doc):
    canvas.saveState()
    w,h=doc.pagesize
    pad=19*mm
    canvas.setFillColor(NAVY)
    canvas.setFont('BodyLabBold',8)
    canvas.drawString(pad,h-15*mm,'PUC MINAS  /  PROJETO DE SOFTWARE  /  LAB03S02')
    canvas.setStrokeColor(BORDER); canvas.setLineWidth(.7)
    canvas.line(pad,h-19*mm,w-pad,h-19*mm)
    canvas.line(pad,17*mm,w-pad,17*mm)
    canvas.setFont('BodyLab',7.4); canvas.setFillColor(GREY)
    canvas.drawCentredString(w/2,12*mm,f'Sistema de Moeda Estudantil  •  Sprint 02  |  Página {doc.page}')
    canvas.restoreState()

class Relatorio(BaseDocTemplate):
    def __init__(self,filename,**kwargs):
        super().__init__(filename,pagesize=A4,**kwargs)
        f=Frame(20*mm,23*mm,A4[0]-40*mm,A4[1]-48*mm,id='A4',leftPadding=0,rightPadding=0,topPadding=4,bottomPadding=0)
        pw,ph=landscape(A3)
        fs=Frame(18*mm,21*mm,pw-36*mm,ph-45*mm,id='A3',leftPadding=0,rightPadding=0,topPadding=4,bottomPadding=0)
        self.addPageTemplates([
          PageTemplate(id='A4',frames=[f],onPage=page_decor,pagesize=A4),
          PageTemplate(id='A3',frames=[fs],onPage=page_decor,pagesize=landscape(A3))])

story=[]
# CAPA
story += [Spacer(1,24*mm),P('PONTIFÍCIA UNIVERSIDADE CATÓLICA DE MINAS GERAIS','overline'),Spacer(1,3*mm),
 P('Curso de Engenharia de Software  ·  Disciplina: Projeto de Software','caption'),
 Spacer(1,17*mm),P('LAB03S02','cover'),Spacer(1,8*mm),
 P('Sistema de Moeda Estudantil: Modelo ER, Persistência e CRUDs Iniciais','title'),
 Spacer(1,11*mm),HRFlowable(width='80%',thickness=3,color=TEAL,hAlign='LEFT'),
 Spacer(1,14*mm),P('LABORATÓRIO 3  ·  SPRINT 02  ·  2º SEMESTRE DE 2026','overline'),
 Spacer(1,15*mm),tbl([
 ['ENTREGA','CONTEÚDO'],
 ['01 — Modelo ER','12 tabelas, associações, cardinalidades e restrições'],
 ['02 — Persistência','SQLite + SQLAlchemy ORM, repositórios e sessões transacionais'],
 ['03 — CRUD Aluno','Interface web, API de cadastro, consulta, alteração e exclusão'],
 ['04 — CRUD Empresa','Interface web, API de cadastro, consulta, alteração e exclusão'],
 ['05 — Verificação','6 testes automatizados e guia de execução']], [49*mm,121*mm]),
 Spacer(1,2*mm),P('Documento técnico e de implementação  •  Versão 1.0  •  Outubro de 2026','caption')]
story.append(PageBreak())
# PG2
story += [sec('1','Objetivo e escopo'),
 P('A LAB03S02 dá continuidade direta à modelagem do relatório LAB03S01_Relatorio_Completo. O enunciado do Laboratório 3, seção 4.2, exige Modelo Entidade-Relacionamento (ER), definição e implementação da estratégia de acesso ao banco de dados e CRUDs iniciais de aluno e empresa parceira, incluindo front-end e comunicação com o back-end.'),
 P('Nesta sprint, a aplicação funcional está concentrada na manutenção cadastral e autenticação. As tabelas para distribuição de moedas, créditos semestrais, vantagens, resgates, cupons e notificações são modeladas, mas suas regras operacionais pertencem à LAB03S03.'),
 P('1.1 Entregas em conformidade com o enunciado','h2'),
 tbl([['Critério','Evidência entregue'],['Modelo ER','Diagrama vetorial (SVG/PDF), PNG, PlantUML, Mermaid e esquema SQL'],['Estratégia de acesso','FastAPI, SQLAlchemy 2 ORM, camada Repository/Service e SQLite'],['CRUD aluno','Criar, consultar, atualizar e excluir; interface HTML + fetch JSON'],['CRUD empresa','Criar, consultar, atualizar e excluir; interface HTML + fetch JSON'],['Validação','Pytest com banco isolado em memória; 6 cenários aprovados']],[51*mm,119*mm]),
 P('1.2 Correspondência com a Sprint 01','h2'),
 bullet('<b>UsuárioSistema:</b> a generalização do Anexo B tornou-se tabela <b>usuarios</b>, com perfis aluno, professor e empresa.'),
 bullet('<b>InstituicaoEnsino:</b> instituição é pré-cadastrada e ligada a alunos e professores.'),
 bullet('<b>ContaMoedas:</b> aluno e professor possuem carteira; empresa não possui saldo.'),
 bullet('<b>Arquitetura MVC:</b> views Jinja2/JavaScript, controllers FastAPI, services/repositories e modelos SQLAlchemy.'),
 P('Fontes: relatório LAB03S01, seções 1, 2, 5 e 6; enunciado do Laboratório 3, seção 4.2.','caption'),
 PageBreak()]
# PG3
story += [sec('2','Modelo Entidade-Relacionamento'),
 P('Foram definidas <b>12 tabelas relacionadas</b>, respeitando as multiplicidades da modelagem UML da Sprint 01. A herança é materializada por uma tabela de credenciais comum (<b>usuarios</b>) e perfis especializados com o mesmo identificador primário/estrangeiro.'),
 tbl([['Grupo','Tabelas / finalidade'],
  ['Acesso e cadastros','instituicoes, usuarios, alunos, professores, empresas_parceiras'],
  ['Moedas e transferências','carteiras, transacoes_moedas, creditos_semestrais'],
  ['Benefícios e comunicação','vantagens, resgates, cupons, notificacoes']], [52*mm,118*mm]),
 P('2.1 Cardinalidades centrais','h2'),
 tbl([['Relacionamento','Cardinalidade'],
 ['Instituição → Aluno / Professor','1 : 0..N (um vínculo institucional obrigatório por perfil)'],
 ['Usuário → Aluno / Professor / Empresa','1 : 0..1 (especialização determinada pelo perfil)'],
 ['Usuário → Carteira','1 : 0..1 (somente aluno e professor na regra de negócio)'],
 ['Empresa → Vantagem','1 : 0..N'],
 ['Aluno → Resgate; Vantagem → Resgate','1 : 0..N'],
 ['Resgate → Cupom','1 : 1 quando concluído'],
 ['Carteira → Transações','0..N nos papéis origem/destino']], [65*mm,105*mm]),
 P('2.2 Restrições de integridade','h2'),
 bullet('Identificadores UUID; chaves estrangeiras institucionais e financeiras, com impedimento de remoção de histórico vinculado.'),
 bullet('UNIQUE para login, CPF/e-mail de aluno, e-mail e CNPJ opcional de empresa e código de cupom.'),
 bullet('CHECK para saldo não negativo, quantidade de moedas e custo de vantagem/resgate positivos.'),
 bullet('UNIQUE (professor_id, semestre) em creditos_semestrais para impedir o mesmo crédito duas vezes.'),
 P('O diagrama ER integral está na página seguinte (formato A3 paisagem para preservar legibilidade); fontes editáveis e exportações estão em docs/diagramas/.','caption'),
 NextPageTemplate('A3'),PageBreak()]
# PG4 (A3 horizontal diagram)
story += [P('ANEXO A — MODELO ER COMPLETO','h1'),P('Representação do banco implementado em SQLAlchemy. PK = chave primária; FK = chave estrangeira; UQ = restrição de unicidade.','caption')]
img=Image(str(ROOT/'docs'/'diagramas'/'modelo_er.png'))
ratio=img.imageHeight/img.imageWidth
maxw=landscape(A3)[0]-42*mm
maxh=landscape(A3)[1]-70*mm
img.drawWidth=min(maxw,maxh/ratio)
img.drawHeight=img.drawWidth*ratio
story.extend([img,Spacer(1,7*mm),P('Figura 1 — Entidades e vínculos. O arquivo SVG pode ser ampliado livremente para leitura de cada atributo.','caption'),NextPageTemplate('A4'),PageBreak()])
# PG5
story += [sec('3','Estratégia de acesso ao banco de dados'),
 P('A estratégia escolhida é <b>Mapeamento Objeto-Relacional (ORM)</b> com SQLAlchemy 2.0 e banco SQLite 3. O domínio é representado em classes Python. Os repositórios realizam consultas declarativas parametrizadas; os serviços coordenam as regras e transações; os controllers expõem a interface HTTP JSON.'),
 P('3.1 Fluxo da requisição','h2'),
 tbl([['Camada','Responsabilidade / arquivo'],
 ['View','templates/*.html e static/js/app.js — interface e consumo fetch'],
 ['Controller','routers/alunos.py e empresas.py — autorização e respostas HTTP'],
 ['Contrato','schemas.py — validação Pydantic, CPF, CNPJ e e-mail'],
 ['Model/Service','services/alunos.py e empresas.py — criação, atualização, exclusão e regras'],
 ['Repository','repositories/alunos.py e empresas.py — consultas ORM'],
 ['Persistência','models.py e database.py — classes mapeadas e sessões SQLite']], [42*mm,128*mm]),
 P('3.2 Operações de persistência e integridade','h2'),
 bullet('No cadastro de aluno, usuário, perfil e carteira com saldo inicial 0 são persistidos dentro da <b>mesma transação</b>; falhas de integridade provocam rollback.'),
 bullet('O cadastro da empresa persiste usuário e perfil parceiro atomicamente; as senhas são armazenadas como <b>PBKDF2-HMAC-SHA256</b> com salt individual.'),
 bullet('SQLite tem integridade referencial explicitamente habilitada (<b>PRAGMA foreign_keys=ON</b>), índices de pesquisa e restrições CHECK/UNIQUE.'),
 bullet('Acesso é restrito ao dono do cadastro. Professor pode consultar estudantes da própria instituição sem visualizar CPF e e-mail.'),
 P('3.3 Reprodutibilidade','h2'),
 P('O banco <b>moeda_estudantil.db</b> é criado automaticamente na primeira execução de python run.py. Um script alternativo de inicialização está em scripts/seed.py e o esquema SQL pode ser auditado em docs/esquema_sqlite.sql.'),
 PageBreak()]
# PG6
story += [sec('4','CRUDs iniciais: aluno e empresa parceira'),
 P('Os CRUDs foram implementados ponta a ponta: formulários HTML, validação cliente/servidor, chamadas JavaScript fetch, controllers REST, serviços e persistência ORM. Cada pessoa autenticada só pode editar ou excluir o próprio cadastro.'),
 P('4.1 Operações REST','h2'),
 tbl([['Entidade','Operação','Endpoint'],
 ['Aluno','Create','POST /api/alunos'],
 ['Aluno','Read (lista e detalhe)','GET /api/alunos e GET /api/alunos/{id}'],
 ['Aluno','Update / Delete','PUT e DELETE /api/alunos/{id}'],
 ['Empresa','Create','POST /api/empresas'],
 ['Empresa','Read (lista e detalhe)','GET /api/empresas e GET /api/empresas/{id}'],
 ['Empresa','Update / Delete','PUT e DELETE /api/empresas/{id}']], [32*mm,57*mm,81*mm]),
 P('4.2 Campos cadastrais implementados','h2'),
 P('<b>Aluno:</b> nome completo, e-mail, CPF, RG, endereço, instituição de ensino pré-cadastrada, curso, login e senha. CPF, e-mail e login são únicos. A alteração do CPF e login não é exposta nesta versão; o usuário pode atualizar os demais campos, instituição e senha.'),
 P('<b>Empresa:</b> nome, e-mail de contato, login e senha obrigatórios; CNPJ e descrição opcionais. Unicidade de e-mail de contato e CNPJ (quando informado). Cada parceiro administra apenas o próprio cadastro.'),
 P('4.3 Autenticação e segurança básica','h2'),
 bullet('Sessão assinada em cookie HTTPOnly/SameSite=Lax; login e logout; perfis verificados nos controllers.'),
 bullet('Mutações POST/PUT/DELETE verificam token anti-CSRF da sessão; senhas não são retornadas pela API.'),
 bullet('HTTP 400/401/403/404/409/422 conforme validação, autenticação, permissão e conflitos de unicidade.'),
 P('O Swagger em /docs documenta contratos e permite inspecionar as rotas; exemplos completos no arquivo docs/API.md.','caption'),
 PageBreak()]
# PG7
story += [sec('5','Interface web e comunicação'),
 P('A camada View foi desenvolvida em HTML semântico, CSS responsivo e JavaScript com <b>fetch</b> nativo. A página obtém o token em GET /api/sessao e envia JSON aos controllers. A resposta do back-end é usada para atualizar os dados ou exibir erro de validação.'),
 tbl([['Tela','Objetivo'],
 ['/','Explica os perfis e encaminha aos cadastros'],
 ['/cadastro/aluno','Criação de aluno com seleção dinâmica de instituição'],
 ['/cadastro/empresa','Criação de empresa parceira com campos mínimos e opcionais'],
 ['/login','Autenticação via login/senha'],
 ['/painel','Dados do dono, edição, exclusão; professor consulta alunos da instituição'],
 ['/parceiros','Lista pública de empresas com apenas nome e descrição']], [48*mm,122*mm]),
 P('5.1 Sequência de cadastro de aluno','h2'),
 tbl([['Passo','Fluxo verificável'],
 ['1','View carrega instituições com GET /api/instituicoes'],
 ['2','Usuário preenche nome, CPF, RG, endereço, curso, login e senha'],
 ['3','JS envia POST /api/alunos com JSON e token anti-CSRF'],
 ['4','Controller chama o serviço e valida os dados de entrada'],
 ['5','ORM persiste usuário, aluno e carteira na mesma transação'],
 ['6','Resposta HTTP 201 orienta usuário ao login']], [25*mm,145*mm]),
 P('A comunicação entre front e back é efetiva; não se trata de telas sem persistência ou dados estáticos.','caption'),
 PageBreak()]
# PG8
story += [sec('6','Verificação funcional e resultados'),
 P('Os testes foram realizados com <b>pytest + TestClient (FastAPI)</b>. Cada cenário usa SQLite em memória isolado, com as mesmas tabelas, restrições e regras da aplicação local.'),
 tbl([['Teste automatizado','Verificação'],
 ['Início e instituições','Páginas, consulta das instituições pré-cadastradas e Swagger'],
 ['CRUD aluno','Create/Read/Update/Delete, hash, login e token anti-CSRF'],
 ['CRUD empresa','Create/Read/Update/Delete, consulta pública sem expor contato'],
 ['Proteção de contas','Professor, aluno e empresa sem privilégios indevidos'],
 ['Validações','Instituição inválida, documento inválido, login duplicado'],
 ['Isolamento institucional','Professor vê apenas alunos vinculados à própria instituição']], [67*mm,103*mm]),
 Spacer(1,5*mm),
 tbl([['Comando de teste','Resultado obtido'],['python -m pytest tests -q','6 passed']], [112*mm,58*mm]),
 P('6.1 Passos para executar no Windows','h2'),
 P('1. Instalar Python 3.11+; abrir o PowerShell na pasta do projeto extraída do ZIP.'),
 P('2. Executar: <b>py -m venv .venv</b> e <b>.\\.venv\\Scripts\\Activate.ps1</b>.'),
 P('3. Executar: <b>python -m pip install -r requirements.txt</b>.'),
 P('4. Executar: <b>python run.py</b> e acessar <b>http://127.0.0.1:8000</b>.'),
 P('5. Criar aluno e empresa pelos formulários, autenticar-se e testar consulta, edição e exclusão. Para testar como professor: <b>professor@demo.local</b> / <b>Demo@12345</b> (ambiente local de demonstração).'),
 P('6. Executar: <b>python -m pytest tests -v</b> para repetir os testes automáticos.'),
 PageBreak()]
# PG9
story += [sec('7','Rastreabilidade e limites de entrega'),
 P('As funcionalidades concluídas nesta sprint cobrem as entregas específicas da seção 4.2. Os demais fluxos, já identificados nos casos de uso e histórias da Sprint 01, foram preservados na modelagem relacional e planejados para a continuação.'),
 tbl([['Origem da Sprint 01','LAB03S02 — Evidência'],
 ['UC01 / HU01 / RN01','Cadastro de aluno com vínculo institucional'],
 ['UC06 / HU04','Cadastro de empresa, com perfil e credenciais'],
 ['UC02 / HU02 / HU16 / RN12','Login, sessão, autorização por perfil'],
 ['HU03 / RN02','Professor pré-cadastrado e vinculado à instituição'],
 ['Modelo de classes, Anexo B','Generalização de usuário e relacionamentos implementados em tabelas'],
 ['Modelo de componentes, Anexo C','Separação MVC + serviços + repositórios ORM'],
 ['HU05–HU15','Estrutura de dados preparada; fluxos financeiros não concluídos']], [72*mm,98*mm]),
 P('7.1 Funcionalidades que pertencem à Sprint 03','h2'),
 bullet('Crédito automático de 1.000 moedas por professor em cada semestre, com idempotência.'),
 bullet('Distribuição de moedas com motivo obrigatório, saldo suficiente e atualização atômica dos saldos.'),
 bullet('Exibição de extrato financeiro completo, cadastro de vantagens com foto e catálogo.'),
 bullet('Resgate, emissão de cupom único e envio de notificações por e-mail para aluno e empresa.'),
 bullet('Apresentação final do protótipo e tutorial de tecnologias (exigências específicas da Sprint 03).'),
 P('7.2 Organização do pacote entregue','h2'),
 P('<b>app/</b> contém o código MVC; <b>tests/</b> contém os testes; <b>docs/diagramas/</b> guarda fontes e exportações do ER; <b>docs/esquema_sqlite.sql</b> contém o DDL; <b>README.md</b> apresenta a execução; <b>referencias/</b> traz o relatório da Sprint 01 e o enunciado. Todos os itens são distribuídos em um único arquivo ZIP.'),
 P('Conclusão: Modelo ER, estratégia ORM efetivamente implementada e CRUDs iniciais com front-end/back-end e persistência funcional estão completos para a LAB03S02.','caption')]

Relatorio(str(OUT),leftMargin=20*mm,rightMargin=20*mm,topMargin=24*mm,bottomMargin=24*mm,
          title='LAB03S02 — Sistema de Moeda Estudantil',author='Relatório acadêmico de Engenharia de Software').build(story)
print('Relatório gerado:',OUT)
