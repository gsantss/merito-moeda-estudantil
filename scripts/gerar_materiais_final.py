"""Gera relatório acadêmico PDF e apresentação PPTX da Sprint 03.
Dependências apenas para geração editorial: reportlab, python-pptx, Pillow.
"""
from pathlib import Path
import textwrap
from xml.sax.saxutils import escape
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image as PDFImage, PageBreak, KeepTogether, HRFlowable)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, landscape
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT/'docs'
DIA = DOCS/'diagramas'
OUT = ROOT/'apresentacao'
OUT.mkdir(exist_ok=True)
NAVY='#12344D'; TEAL='#008C87'; GOLD='#F3C26C'; INK='#1E3444'; MUTED='#617885'; LIGHT='#F2F7F7'

def rgb(s):
    s=s.strip('#');return RGBColor(*[int(s[i:i+2],16) for i in (0,2,4)])

def c(s):return colors.HexColor(s)

def ptext(s):return escape(s).replace('\n','<br/>')

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverBig3',fontName='Helvetica-Bold',fontSize=27,leading=33,textColor=c(NAVY),spaceAfter=14))
styles.add(ParagraphStyle(name='CoverSub3',fontName='Helvetica',fontSize=13,leading=20,textColor=c(MUTED),spaceAfter=16))
styles.add(ParagraphStyle(name='Header3',fontName='Helvetica-Bold',fontSize=15,leading=19,textColor=c(NAVY),spaceBefore=14,spaceAfter=10,keepWithNext=True))
styles.add(ParagraphStyle(name='Sub3',fontName='Helvetica-Bold',fontSize=10,leading=14,textColor=c(TEAL),spaceBefore=10,spaceAfter=5,keepWithNext=True))
styles.add(ParagraphStyle(name='Body3',fontName='Helvetica',fontSize=9.3,leading=14,textColor=c(INK),spaceAfter=7))
styles.add(ParagraphStyle(name='Small3',fontName='Helvetica',fontSize=8.2,leading=12,textColor=c(MUTED),spaceAfter=6))
styles.add(ParagraphStyle(name='Cell3',fontName='Helvetica',fontSize=7.5,leading=10,textColor=c(INK)))
styles.add(ParagraphStyle(name='CellHead3',fontName='Helvetica-Bold',fontSize=8,leading=11,textColor=colors.white))

story=[]
def add(s):story.append(Paragraph(s,styles['Body3']))
def small(s):story.append(Paragraph(s,styles['Small3']))
def h(s):story.append(Paragraph(s,styles['Header3']))
def sh(s):story.append(Paragraph(s,styles['Sub3']))
def table(headers,rows,widths=None):
    data=[[Paragraph(ptext(str(i)),styles['CellHead3']) for i in headers]]
    for row in rows:data.append([Paragraph(ptext(str(i)),styles['Cell3']) for i in row])
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),c(NAVY)),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,c('#F1F6F8')]),
                ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,c('#D7E4E5')),
                ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(t);story.append(Spacer(1,.3*cm))
def pic(path,max_w=16.5*cm,max_h=20*cm):
    with Image.open(path) as im:w,h1=im.size
    scale=min(max_w/w,max_h/h1);story.append(PDFImage(str(path),width=w*scale,height=h1*scale,hAlign='CENTER'))
    story.append(Spacer(1,.35*cm))

def footer(canvas,doc):
    canvas.saveState();w,h1=doc.pagesize
    canvas.setStrokeColor(c('#DCE8E7'));canvas.line(1.9*cm,1.5*cm,w-1.9*cm,1.5*cm)
    canvas.setFont('Helvetica',8);canvas.setFillColor(c(MUTED))
    canvas.drawString(1.9*cm,1.14*cm,'PUC Minas  |  Projeto de Software  |  LAB03S03')
    canvas.drawRightString(w-1.9*cm,1.14*cm,f'Página {doc.page}')
    canvas.restoreState()

doc=SimpleDocTemplate(str(DOCS/'LAB03S03_Relatorio_Completo.pdf'),pagesize=A4,
                      leftMargin=1.9*cm,rightMargin=1.9*cm,topMargin=1.9*cm,bottomMargin=1.85*cm,
                      title='LAB03S03 - Protótipo final - Moeda Estudantil',author='Projeto de Software - PUC Minas')
story.append(Spacer(1,1.15*cm));small('PONTIFÍCIA UNIVERSIDADE CATÓLICA DE MINAS GERAIS  ·  ENGENHARIA DE SOFTWARE')
story.append(Spacer(1,1.4*cm));story.append(Paragraph('LAB03S03',styles['CoverBig3']))
story.append(Paragraph('Sistema de Moeda Estudantil<br/>Protótipo final, MVC e persistência',styles['CoverBig3']))
story.append(Paragraph('Laboratório 3 · Sprint 03 · Segundo semestre de 2026',styles['CoverSub3']))
story.append(Spacer(1,.7*cm))
table(['ITEM','ENTREGA'],[['01','CRUD final de Aluno e Empresa Parceira (interface e API)'],['02','Regras do domínio: semestres, moedas, vantagens, resgates e cupons'],['03','Arquitetura MVC e camada de persistência com SQLAlchemy ORM'],['04','Testes automatizados, tutorial de tecnologias e apresentação final']],[2.2*cm,14.6*cm])
small('Base: LAB03S01_Relatorio_Completo, LAB03S02_Completo e enunciado do Laboratório 3, item 4.3. Solução de caráter acadêmico, destinada à execução local.')
story.append(Spacer(1,3.5*cm))
small('Versão 3.0 · Outubro de 2026  |  Código-fonte, diagramas e apresentação no mesmo pacote ZIP.')
story.append(PageBreak())
h('1. Objetivo, escopo e continuidade')
add('Este documento apresenta a implementação final do Sistema de Moeda Estudantil. O enunciado estabelece para LAB03S03 os CRUDs definitivos de aluno e empresa parceira e a apresentação da arquitetura e da persistência. O capítulo de apresentação final também solicita um protótipo aderente aos requisitos, arquitetura MVC, modelos atualizados e um tutorial das tecnologias em até 20 minutos.')
table(['ETAPA','CONTRIBUIÇÃO'],[
 ['LAB03S01','Casos de uso, 16 histórias do usuário, diagrama de classes e de componentes MVC.'],
 ['LAB03S02','Modelo ER, esquema SQL, ORM e CRUDs iniciais de aluno e empresa parceira.'],
 ['LAB03S03','Finalização de CRUDs e integração completa de créditos, transferências, extrato, catálogo, resgates, cupons e notificação.']], [2.7*cm,14.1*cm])
h('2. Requisitos implementados')
table(['PERFIL','FLUXOS DA VERSÃO FINAL'],[
 ['Aluno','Cadastrar, autenticar, editar e excluir/desativar cadastro; consultar saldo/extrato; navegar pelas vantagens, resgatar, consultar cupons.'],
 ['Professor','Usar conta pré-cadastrada, receber crédito semestral, consultar alunos da própria instituição, distribuir moedas com motivo e saldo suficiente, consultar extrato.'],
 ['Empresa parceira','Cadastrar, autenticar, editar e excluir/desativar cadastro; manter vantagens com foto/custo/descrição, conferir e baixar cupons.'],
 ['Serviços','Job de 1.000 moedas por semestre; outbox de e-mail com execução SMTP desacoplada do débito.']], [3.15*cm,13.65*cm])
sh('Premissas relevantes')
add('Como o enunciado não define as datas exatas do semestre, a identificação é informada ao agendador no formato AAAA/1 ou AAAA/2. Como não há dados detalhados para a empresa, foram mantidos nome e e-mail como campos obrigatórios, com CNPJ e descrição opcionais. Professores não têm cadastro público; a conta de demonstração é inserida pelo seed local.')
story.append(PageBreak())
h('3. Arquitetura do sistema (MVC)')
add('A arquitetura mantém a separação existente desde o diagrama de componentes da Sprint 01: interface web (View), endpoints REST e segurança (Controller), regras e entidades de domínio (Model), repositórios, ORM e banco de dados (Infraestrutura).')
pic(DIA/'arquitetura_final.png',max_w=16.7*cm,max_h=10.4*cm)
table(['CAMADA','TECNOLOGIA / IMPLEMENTAÇÃO'],[
 ['View','Jinja2 + HTML5 + CSS3 + JavaScript (fetch), páginas do aluno, professor e empresa.'],
 ['Controller','FastAPI / Pydantic, API HTTP e respostas JSON com códigos de erro.'],
 ['Model','SQLAlchemy ORM, serviços de cadastro, carteira, créditos, distribuição e resgates.'],
 ['Persistência','SQLite com índices, foreign keys, constraints, transações commit/rollback.'],
 ['Infraestrutura','Job de crédito semestral, outbox e SMTP configurável.']], [3*cm,13.8*cm])
story.append(PageBreak())
h('4. Modelo ER e esquema físico')
add('O modelo relacional contempla 12 tabelas. O diagrama apresentado na Sprint 02 foi preservado: as estruturas previstas para as operações futuras já estavam definidas. O SQL final está disponível em docs/esquema_sqlite.sql e os diagramas editáveis no diretório docs/diagramas.')
pic(DIA/'modelo_er.png',max_w=16.65*cm,max_h=16.4*cm)
small('Principais integridades: login, CPF, e-mail e código de cupom únicos; saldos não negativos; custos e quantidades positivos; idempotência de crédito por (professor, semestre).')
story.append(PageBreak())
h('5. Estratégia de persistência com ORM')
add('SQLAlchemy 2.x permite representar tabelas como classes Python e consultas em expressões do ORM, desacoplando a regra de negócio da sintaxe SQL. A camada app/database.py mantém o mecanismo de conexão e a fábrica de sessões. Cada requisição obtém sua própria sessão e os serviços controlam transações atômicas.')
table(['ELEMENTO','EXEMPLO / GARANTIA'],[
 ['Mapeamento','Usuario, Aluno, Professor, EmpresaParceira, Carteira, TransacaoMoedas, Vantagem, Resgate, Cupom e Notificacao são classes mapeadas.'],
 ['Chaves','UUID strings; PK/FK; relacionamentos 1:1, 1:N, N:1.'],
 ['Atomicidade','UPDATE condicional de saldo; commit único ou rollback integral em falha.'],
 ['Unicidade','UniqueConstraint(professor_id, semestre) impede crédito duplo; código de cupom UNIQUE.'],
 ['Consistência','Foreign keys do SQLite ativadas e checks para custo, saldo e quantidade.']], [3.2*cm,13.6*cm])
h('6. Fluxo financeiro e integridade')
pic(DIA/'fluxo_transacoes.png',max_w=14.5*cm,max_h=12.2*cm)
add('O envio de e-mail não integra a transação SQL: são criadas notificações pendentes no mesmo commit, e um processo separado tenta realizar o envio SMTP. Isso evita repetir moedas ou resgates quando o servidor de e-mail falha.')
story.append(PageBreak())
h('7. CRUDs finais de Aluno e Empresa')
table(['OPERAÇÃO','ALUNO','EMPRESA PARCEIRA'],[
 ['Create','POST /api/alunos','POST /api/empresas'],
 ['Read','GET /api/alunos/{id}','GET /api/empresas/{id}'],
 ['Update','PUT /api/alunos/{id}','PUT /api/empresas/{id}'],
 ['Delete','DELETE /api/alunos/{id}','DELETE /api/empresas/{id}'],
 ['Histórico vinculado','PATCH /api/alunos/{id}/desativar','PATCH /api/empresas/{id}/desativar']], [3.1*cm,6.75*cm,6.95*cm])
add('O usuário pode editar seus próprios dados no painel. Para evitar perda de histórico financeiro, exclusão física só ocorre quando não existem vínculos impeditivos. Em caso contrário, a conta pode ser desativada. A empresa desativada também deixa de oferecer vantagens no catálogo.')
sh('Validação e autorização')
add('No back-end: CPF validado, e-mail e login únicos, instituição ativa, senha hasheada, autenticação com cookies de sessão assinados, CSRF e autorização por perfil e propriedade do cadastro. O front-end apresenta os formulários, mas não substitui a autorização realizada no servidor.')
h('8. Fluxos principais de uso')
table(['ETAPA','SEQUÊNCIA'],[
 ['1. Cadastro','Aluno escolhe instituição; empresa informa contato; ambos definem login/senha.'],
 ['2. Crédito','Agendador executa job por semestre; professor ativo recebe 1.000 moedas uma vez.'],
 ['3. Distribuição','Professor escolhe aluno da instituição; informa valor e motivo; débito/crédito/extrato/outbox.'],
 ['4. Vantagem','Empresa cria vantagem com título, descrição, foto e custo positivo.'],
 ['5. Resgate','Aluno escolhe vantagem; sistema debita, gera cupom único e prepara dois e-mails.'],
 ['6. Troca','Empresa confere código, executa baixa única e histórico permanece preservado.']], [3.2*cm,13.6*cm])
story.append(PageBreak())
h('9. Testes e evidências')
add('A suíte automatizada é executada localmente com pytest e httpx/TestClient. Durante a construção, os testes foram executados com sucesso. Cada caso usa um banco SQLite isolado em memória, sem depender de dados reais.')
table(['CENÁRIO VALIDADO','RESULTADO'],[
 ['Páginas, instituições, documentação OpenAPI','Aprovado'],
 ['CRUD final de aluno, autenticação, edição e exclusão','Aprovado'],
 ['CRUD final de empresa, privacidade de informações','Aprovado'],
 ['Restrições por perfil e propriedade','Aprovado'],
 ['Validação de CPF/CNPJ, login e vínculo institucional','Aprovado'],
 ['Professor enxerga só alunos da própria instituição','Aprovado'],
 ['Crédito semestral acumulativo e idempotente','Aprovado'],
 ['Distribuição atômica, justificativa, insuficiência de saldo e outbox','Aprovado'],
 ['Vantagem, resgate, cupom único, conferência e baixa única','Aprovado'],
 ['Edição de vantagem e controle cruzado de perfis','Aprovado'],
 ['Sem SMTP não há envio fictício / outbox continua pendente','Aprovado']], [12.4*cm,4.4*cm])
add('<b>Comando para reproduzir:</b> <font face="Courier">python -m pytest -q</font>. O resultado deve ser verificado no ambiente da banca. A entrega inclui código-fonte dos testes e não substitui testes de carga, segurança e produção.')
h('10. Limitações conhecidas')
add('O backend envia e-mails reais apenas se o administrador configurar SMTP e executar o processador. O crédito semestral depende de agendamento externo (manual por script no cenário local). A foto de vantagem é informada por URL HTTPS/HTTP, sem upload binário. O SQLite e a chave de sessão de exemplo atendem à demonstração local; para produção seriam necessários HTTPS, segredos novos, migrações, observabilidade, antifraude e infraestrutura adicional.')
story.append(PageBreak())
h('11. Guia de demonstração e apresentação')
add('<b>Preparação:</b> criar ambiente virtual, instalar requirements.txt, executar <font face="Courier">python -m scripts.preparar_demo</font>, iniciar com <font face="Courier">python run.py</font> ou iniciar_windows.ps1. Na instalação local abrir http://127.0.0.1:8000 e /docs.')
sh('Sequência de demonstração sugerida')
add('1. Entrar como professor@demo.local; conferir crédito de 1.000; enviar 200 moedas para aluno.demo com motivo. 2. Entrar como aluno.demo; conferir o extrato e resgatar uma vantagem. 3. Entrar como empresa.demo; conferir cupom e dar baixa. 4. Mostrar como os registros foram persistidos e como os e-mails permaneceram pendentes quando não existe SMTP.')
small('Login correto do professor de demonstração: professor@demo.local. Os logins de aluno e empresa são aluno.demo e empresa.demo. Senha fictícia em todos os casos: Demo@12345. Acessos de demonstração, nunca para uso público.')
h('12. Conclusão')
add('A LAB03S03 evolui os modelos da Sprint 01 e a persistência/CRUD da Sprint 02 até um protótipo MVC executável, com os casos de uso essenciais implementados e validáveis. CRUDs finais, crédito semestral, distribuição, resgate, cupons e controle de acesso compartilham o mesmo modelo ER e seguem os invariantes documentados. O arquivo de apresentação contempla a arquitetura, o tutorial das tecnologias e a demonstração final de 20 minutos.')
h('13. Arquivos de entrega')
table(['PASTA / ARQUIVO','CONTEÚDO'],[
 ['app/','MVC: models, services, routers, templates, CSS e JS.'],
 ['tests/','11 casos automatizados de cadastro, segurança e operações.'],
 ['docs/','Relatório, arquitetura/persistência, API, rastreabilidade, esquema SQL e diagramas.'],
 ['apresentacao/','Slides PPTX/PDF e roteiro de 20 minutos.'],
 ['scripts/','Seed demo, crédito semestral, notificações SMTP e gerador de materiais.'],
 ['referencias/','Documentos de origem LAB03S01 e enunciado, mais relatório S02.']], [4*cm,12.8*cm])
doc.build(story,onFirstPage=footer,onLaterPages=footer)

# Presentation
prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
blank=prs.slide_layouts[6]
def rect(sl,x,y,w,h,fill,radius=False,border=None):
    sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
    sh.line.fill.background() if not border else None
    if border:sh.line.color.rgb=rgb(border)
    return sh

def text(sl,content,x,y,w,h,size=16,color=INK,bold=False,align=None,font='Aptos',margin=.03):
    sh=sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf=sh.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=Inches(margin);tf.margin_top=Inches(margin);tf.margin_right=Inches(margin);tf.margin_bottom=Inches(margin)
    p=tf.paragraphs[0];p.alignment=align or PP_ALIGN.LEFT
    for i,line in enumerate(content.split('\n')):
        q=p if i==0 else tf.add_paragraph();q.text=line;q.font.name=font;q.font.size=Pt(size);q.font.bold=bold;q.font.color.rgb=rgb(color);q.space_after=Pt(7)
    return sh

def base(title,kicker='',dark=False):
    sl=prs.slides.add_slide(blank)
    rect(sl,0,0,13.333,7.5,NAVY if dark else '#F8FAFA')
    rect(sl,0,0,.13,7.5,TEAL)
    if kicker:text(sl,kicker.upper(),.7,.38,10,.3,12,GOLD if dark else TEAL,True)
    text(sl,title,.7,.92,12,1.05,32,'#FFFFFF' if dark else NAVY,True)
    rect(sl,.73,6.93,11.8,.012,'#476579' if dark else '#DCE9E9')
    text(sl,'PUC Minas · Projeto de Software · LAB03S03',.73,7.03,9,.25,10,'#B0C7D0' if dark else MUTED)
    text(sl,str(len(prs.slides)).zfill(2),12.05,7.03,.6,.23,10,GOLD if dark else TEAL,True,PP_ALIGN.RIGHT)
    return sl

def pill(sl,s,x,y,w=None,fill='#E6F4F2',color=TEAL):
    w=w or max(1.4,len(s)*.093+.5);rect(sl,x,y,w,.46,fill,True);text(sl,s,x+.14,y+.095,w-.28,.24,11,color,True)

def bulletbox(sl,heading,bullets,x,y,w,h,fill='#FFFFFF'):
    rect(sl,x,y,w,h,fill,True)
    text(sl,heading,x+.3,y+.28,w-.6,.47,18,NAVY,True)
    yy=y+.95
    for b in bullets:
        text(sl,'• '+b,x+.32,yy,w-.65,.68 if len(b)>65 else .45,13,INK)
        yy+=.76 if len(b)>65 else .58

def image_slide(sl,path,x,y,w,h):
    with Image.open(path) as i:iw,ih=i.size
    sw=w/iw;sh=h/ih;scale=min(sw,sh)
    width,height=iw*scale,ih*scale
    sl.shapes.add_picture(str(path), Inches(x+(w-width)/2), Inches(y+(h-height)/2), width=Inches(width),height=Inches(height))

sl=base('Sistema de Moeda Estudantil','Entrega final | Sprint 03',True)
text(sl,'Protótipo MVC · CRUDs finais · Persistência · Tutorial',.73,2.47,11,1.13,25,'#F1F8F8',True)
rect(sl,.75,4.3,7.55,.1,TEAL)
text(sl,'LABORATÓRIO 3  /  2º SEMESTRE 2026',.75,4.73,9,.44,15,GOLD,True)
text(sl,'Apresentação demonstrativa: 20 minutos',.75,5.49,10,.48,16,'#C8DBE0')
sl=base('O problema que o sistema resolve','01 · Contexto')
bulletbox(sl,'Reconhecimento por mérito',['Professor recompensa atitudes com moedas virtuais.','Aluno acumula saldo, acompanha extrato e troca moedas por benefícios.','Empresa parceira publica vantagens e confirma cupons.'],.75,2.02,7.05,4.25)
rect(sl,8.18,2.02,4.35,4.25,NAVY,True);text(sl,'PROFESSOR\n↓\nALUNO\n↓\nEMPRESA PARCEIRA',8.65,2.59,3.4,3.2,27,'#FFFFFF',True,PP_ALIGN.CENTER)
sl=base('Da modelagem ao protótipo final','02 · Evolução das sprints')
for x,n,t,b in [(.75,'01','Modelagem',['Casos de uso','Histórias','Classes + MVC']),(5,'02','Persistência',['Modelo ER','SQLAlchemy + SQLite','CRUD inicial']),(9.23,'03','Entrega final',['CRUD concluído','Moedas + resgate','Slides + testes'])]:
    rect(sl,x,2.05,3.35,4.23,'#FFFFFF',True);pill(sl,'SPRINT '+n,x+.27,2.42,1.55);text(sl,t,x+.27,3.15,2.85,.55,23,NAVY,True)
    for i,v in enumerate(b):text(sl,'✓ '+v,x+.27,4.05+i*.55,2.85,.41,14,INK)
sl=base('O que foi entregue','03 · Escopo da LAB03S03')
bulletbox(sl,'Cadastro e acesso',['CRUD final de Aluno e Empresa Parceira.','Autenticação por perfis com validações de entrada.','Desativação segura quando houver dados vinculados.'],.72,2.08,5.85,4.12)
bulletbox(sl,'Domínio completo',['Crédito semestral + transferência de moedas.','Vantagens com foto, custo e descrição.','Resgate, cupom único e notificações em fila.'],6.77,2.08,5.85,4.12)
sl=base('Arquitetura MVC implementada','04 · Visão de componentes')
image_slide(sl,DIA/'arquitetura_final.png',.55,1.88,12.26,4.84)
sl=base('Tecnologias e suas responsabilidades','05 · Tutorial técnico')
for i,(t,b) in enumerate([('FastAPI','Controllers / OpenAPI / sessão'),('Jinja2 + JS','Views e comunicação fetch'),('SQLAlchemy','Modelo + ORM + transações'),('SQLite','Banco local, constraints e chaves')]):
    x=.75+(i%2)*6.1;y=2.05+(i//2)*2.0;rect(sl,x,y,5.68,1.67,'#FFFFFF',True);pill(sl,t,x+.25,y+.22,2.15);text(sl,b,x+.25,y+.88,5.15,.48,17,INK)
sl=base('Como funciona o padrão MVC no código','06 · Tutorial técnico')
bulletbox(sl,'A requisição atravessa 4 camadas',['View: formulário HTML → JavaScript fetch.','Controller: rota /api/distribuicoes autoriza e valida payload.','Model: financeiro.distribuir aplica regras do domínio.','Persistência: SQLAlchemy emite UPDATE/INSERT e COMMIT.'],.75,2,11.85,4.46)
sl=base('Modelo Entidade-Relacionamento','07 · Persistência')
image_slide(sl,DIA/'modelo_er.png',.7,1.82,11.95,4.96)
sl=base('Como protegemos a integridade','08 · Persistência')
bulletbox(sl,'Banco e transações',['12 tabelas mapeadas com SQLAlchemy ORM.','CHECK(saldo >= 0), FOREIGN KEY e UNIQUE por CPF, login e cupom.','Débito condicional: saldo somente diminui quando suficiente.','Commit atômico; rollback impede transferência ou resgate parcial.'],.75,2.05,11.83,4.35)
sl=base('CRUDs finais no painel','09 · Funcionalidades')
bulletbox(sl,'Aluno',['Cadastro com CPF e instituição válida.','Consultas e edição de dados próprios.','Exclusão ou desativação preservando histórico.'],.75,2.05,5.76,4.24)
bulletbox(sl,'Empresa parceira',['Cadastro de nome e contato.','Edição e exclusão/desativação do próprio perfil.','Gestão de vantagens publicadas no catálogo.'],6.79,2.05,5.76,4.24)
sl=base('Crédito semestral','10 · RN03 / RN04')
rect(sl,.75,2.03,4.3,4.17,NAVY,True);text(sl,'1.000',1.14,2.56,3.52,1.17,59,'#FFFFFF',True,PP_ALIGN.CENTER);text(sl,'moedas por semestre',1.14,4.03,3.52,.82,21,GOLD,True,PP_ALIGN.CENTER)
bulletbox(sl,'Regras',['Saldo anterior é acumulado.','Semestre identificado por AAAA/1 ou AAAA/2.','Unicidade professor + semestre evita duplo crédito.','Agendamento via comando externo configurado.'],5.34,2.03,7.25,4.17)
sl=base('Distribuição de moedas','11 · RN05 a RN08')
bulletbox(sl,'Professor → Aluno',['Selecionar aluno da mesma instituição.','Informar quantidade inteira positiva e motivo.','Verificar saldo antes de debitar o professor.','Creditar aluno, registrar extrato e notificação pendente.'],.75,2.08,11.82,4.16)
sl=base('Resgate e conferência presencial','12 · RN09 a RN11')
for x,n,title,b in [(.75,'1','Escolha','Aluno seleciona vantagem ativa'),(3.83,'2','Débito','Sistema verifica saldo e desconta'),(6.91,'3','Cupom','Código randômico único'),(9.99,'4','Troca','Empresa confere e baixa uma vez')]:
    rect(sl,x,2.65,2.58,3.33,'#FFFFFF',True);pill(sl,n,x+.23,3,.6);text(sl,title,x+.21,3.83,2.14,.47,19,NAVY,True);text(sl,b,x+.21,4.59,2.12,1.05,14,INK)
sl=base('Notificações sem duplicar moedas','13 · Outbox e SMTP')
bulletbox(sl,'Processo confiável',['A transação salva duas notificações para cupom, uma para o aluno e outra para a empresa.','Mensagens ficam pendentes até o envio pelo worker SMTP.','Falha no e-mail não reverte nem repete débito/crédito.','Sem configuração SMTP, nenhuma entrega de e-mail é simulada como real.'],.75,2.03,11.84,4.31)
sl=base('Segurança e proteção dos dados','14 · Segurança')
bulletbox(sl,'Regras implementadas',['PBKDF2-SHA256 com salt individual para senhas.','Cookie de sessão HTTPOnly e token anti-CSRF.','Autorização por perfil no backend: aluno, professor e empresa.','Professor acessa somente estudantes de sua instituição.','Cadastro com histórico fica preservado por desativação.'],.75,2.06,11.83,4.45)
sl=base('Testes automatizados','15 · Qualidade')
rect(sl,.76,2.02,3.8,4.23,NAVY,True);text(sl,'11',1.19,2.8,2.96,1.4,86,'#FFFFFF',True,PP_ALIGN.CENTER);text(sl,'testes aprovados',1.06,4.58,3.15,.56,19,GOLD,True,PP_ALIGN.CENTER)
bulletbox(sl,'Cenários',['CRUD / autenticação / perfis.','Semestre idempotente e acumulativo.','Saldo insuficiente sem movimentação parcial.','Resgate, cupom único e uso único.','Notificação pendente sem servidor SMTP.'],4.82,2.02,7.7,4.23)
sl=base('Como executar e reproduzir','16 · Tutorial prático')
bulletbox(sl,'No terminal',['python -m venv .venv','pip install -r requirements.txt','python -m scripts.preparar_demo','python run.py','python -m pytest -q'],.74,2.02,7.04,4.4)
rect(sl,8.03,2.02,4.52,4.4,'#E6F4F2',True);text(sl,'Abrir no navegador',8.4,2.56,3.71,.55,18,NAVY,True);text(sl,'localhost:8000\nlocalhost:8000/docs',8.37,3.45,3.93,1.45,19,TEAL,True)
sl=base('Demonstração ao vivo','17 · Jornada completa')
bulletbox(sl,'Do professor à empresa',['Professor: conferir saldo e distribuir moedas ao aluno.','Aluno: conferir crédito, escolher vantagem e resgatar.','Empresa: conferir o código do cupom e realizar a baixa.','Comprovar extrato e registros pendentes no banco.'],.75,2.02,11.86,4.31)
sl=base('Limites do protótipo e evolução','18 · Responsabilidade técnica')
bulletbox(sl,'Definições para produção',['SMTP externo precisa ser configurado para entrega real.','Job semestral depende de agendador local ou de nuvem.','Trocar chave de sessão de demo, ativar HTTPS e rate limiting.','SQLite é adequado à demonstração, não a um backend escalável.'],.75,2.04,11.87,4.33)
sl=base('Conclusão','19 · Encerramento',True)
text(sl,'Modelos atualizados + aplicação funcional + persistência consistente.',.82,2.57,11.69,1.4,28,'#FFFFFF',True,PP_ALIGN.CENTER)
pill(sl,'LAB03S03 CONCLUÍDA',5.04,4.47,3.15,TEAL,'#FFFFFF')
text(sl,'Perguntas?',.82,5.65,11.69,.61,20,GOLD,True,PP_ALIGN.CENTER)
prs.save(str(OUT/'LAB03S03_Apresentacao_Final_20min.pptx'))
print('Relatório e PPTX gerados:',len(prs.slides),'slides')
