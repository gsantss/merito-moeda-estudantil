"""Gera DDL fiel ao ORM e diagrama ER SVG/PNG usando Graphviz (opcional)."""
from pathlib import Path
from sqlalchemy.schema import CreateIndex, CreateTable
from sqlalchemy.dialects import sqlite
from app.database import Base
from app import models  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'docs'

def main():
    dialeto = sqlite.dialect()
    texto = ['-- Esquema gerado automaticamente do ORM SQLAlchemy (LAB03S02)',
             '-- Banco SQLite 3. As chaves estrangeiras exigem PRAGMA foreign_keys=ON.',
             'PRAGMA foreign_keys=ON;', '']
    for tabela in Base.metadata.sorted_tables:
        texto.append(str(CreateTable(tabela).compile(dialect=dialeto)) + ';')
        for indice in tabela.indexes:
            texto.append(str(CreateIndex(indice).compile(dialect=dialeto)) + ';')
        texto.append('')
    (DEST / 'esquema_sqlite.sql').write_text('\n'.join(texto), encoding='utf-8')
    try:
        from graphviz import Digraph
    except ImportError:
        print('Graphviz Python ausente; DDL gerado, diagrama opcional não renderizado.')
        return
    dot = Digraph('ModeloER', filename=str(DEST/'diagramas'/'modelo_er'), format='svg')
    dot.attr(rankdir='LR', splines='spline', bgcolor='#ffffff', pad='0.4', nodesep='0.9', ranksep='1.4',
             fontname='DejaVu Sans', label='SISTEMA DE MOEDA ESTUDANTIL  |  MODELO ER  |  LAB03S02',
             labelloc='t', fontsize='22', fontcolor='#12344d')
    dot.attr('node', shape='plain')
    cores = {'instituicoes':'#254f68','usuarios':'#254f68','alunos':'#254f68',
             'professores':'#254f68','empresas_parceiras':'#254f68',
             'carteiras':'#007e81','transacoes_moedas':'#007e81','creditos_semestrais':'#007e81',
             'vantagens':'#b17c3b','resgates':'#b17c3b','cupons':'#b17c3b','notificacoes':'#b17c3b'}
    resumo = {
       'instituicoes':['id (PK)', 'nome (UQ)', 'ativa'],
       'usuarios':['id (PK)', 'login (UQ)', 'senha_hash', 'perfil | ativo'],
       'alunos':['id (PK, FK)', 'instituicao_id (FK)', 'nome | email (UQ)', 'cpf (UQ) | rg', 'endereco | curso'],
       'professores':['id (PK, FK)','instituicao_id (FK)','nome | cpf (UQ)','departamento'],
       'empresas_parceiras':['id (PK, FK)', 'nome','email_contato (UQ)','cnpj (UQ) | descricao'],
       'carteiras':['id (PK)','usuario_id (FK, UQ)','saldo >= 0'],
       'transacoes_moedas':['id (PK)','origem_carteira_id (FK)','destino_carteira_id (FK)','tipo | quantidade > 0','motivo | semestre'],
       'creditos_semestrais':['id (PK)','professor_id (FK)','semestre','transacao_id (FK, UQ)'],
       'vantagens':['id (PK)','empresa_id (FK)','titulo | descricao','foto_url | custo > 0'],
       'resgates':['id (PK)','aluno_id (FK)','vantagem_id (FK)','transacao_id (FK, UQ)'],
       'cupons':['id (PK)','resgate_id (FK, UQ)','codigo (UQ)'],
       'notificacoes':['id (PK)','transacao_id (FK)','cupom_id (FK)','destinatario | status'],
    }
    for key, rows in resumo.items():
        html = '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" COLOR="#c9d6da">'
        html += f'<TR><TD BGCOLOR="{cores[key]}"><FONT COLOR="white" FACE="DejaVu Sans" POINT-SIZE="13"><B>{key.upper()}</B></FONT></TD></TR>'
        for linha in rows:
            html += f'<TR><TD ALIGN="LEFT" BGCOLOR="#f7fafb"><FONT FACE="DejaVu Sans" POINT-SIZE="10">{linha.replace(">", "&gt;")}</FONT></TD></TR>'
        html += '</TABLE>'
        dot.node(key, label=f'<{html}>')
    relacoes = [
      ('instituicoes','alunos','1:N'),('instituicoes','professores','1:N'),
      ('usuarios','alunos','1:0..1'),('usuarios','professores','1:0..1'),('usuarios','empresas_parceiras','1:0..1'),
      ('usuarios','carteiras','1:0..1'),('carteiras','transacoes_moedas','origem/destino'),
      ('professores','creditos_semestrais','1:N'),('transacoes_moedas','creditos_semestrais','1:0..1'),
      ('empresas_parceiras','vantagens','1:N'),('alunos','resgates','1:N'),
      ('vantagens','resgates','1:N'),('transacoes_moedas','resgates','1:0..1'),
      ('resgates','cupons','1:1'),('transacoes_moedas','notificacoes','0:N'),('cupons','notificacoes','0:N'),
    ]
    for a,b,rel in relacoes:
        dot.edge(a,b,label=rel,color='#8aa0a8',fontname='DejaVu Sans',fontsize='9',arrowsize='0.55')
    dot.save()
    for fmt in ('svg','png','pdf'):
        try: dot.render(format=fmt,cleanup=False, quiet=True)
        except Exception as exc: print('Não foi possível gerar',fmt,exc)
    print('Arquivos de esquema/diagrama gerados.')

if __name__ == '__main__': main()
