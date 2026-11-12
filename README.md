# LAB03S03 — Sistema de Moeda Estudantil | Protótipo Final

**PUC Minas · Engenharia de Software · Projeto de Software · Laboratório 3 · 2º semestre de 2026**

Esta é a **Sprint 03 completa**, construída sobre o código e o banco da LAB03S02, preservando a modelagem da LAB03S01. O enunciado exige os CRUDs finais de aluno e empresa, arquitetura MVC e explicação da persistência. A apresentação final pede ainda que o protótipo atenda às regras de negócio da moeda estudantil e apresente um tutorial das tecnologias escolhidas.

## Conteúdo da entrega

- **Protótipo funcional**: FastAPI + Jinja2 + CSS + JavaScript + SQLAlchemy + SQLite. Interface em português.
- **CRUD final de aluno e empresa parceira**: inclusão, consulta, edição, exclusão física quando permitida ou desativação com histórico; validação de CPF/CNPJ, instituição e perfis.
- **Autenticação e autorização**: sessão HTTPOnly, PBKDF2-SHA256 com salt, proteção CSRF, autorização por usuário e perfil.
- **Carteiras e extratos**: saldo de aluno/professor e histórico de crédito, distribuição e resgate.
- **Crédito semestral**: 1.000 moedas acumuláveis, uma vez por professor por semestre, executado por job externo.
- **Distribuição**: professor → aluno da instituição, motivo obrigatório, saldo positivo, débito/crédito e notificação gravados juntos.
- **Vantagens**: criação, edição, desativação e catálogo público com título, custo, foto e descrição.
- **Resgate**: validação de saldo, débito indivisível, cupom aleatório único e notificações para aluno e empresa.
- **Uso de cupom**: empresa dona da vantagem pode confirmar e baixar um cupom uma única vez.
- **Material acadêmico**: relatório final de 8 páginas, ER, arquitetura, fluxo transacional, slide deck de 20 páginas e roteiro de 20 minutos.
- **Testes**: 11 testes automatizados aprovados na preparação da entrega.

## 1. Requisitos

- Python 3.11 ou superior (recomendado 3.12/3.13) com `pip`.
- Windows 10/11 com PowerShell, ou macOS/Linux com shell.
- Internet na primeira instalação das dependências e para carregar imagens externas do catálogo (opcional).
- Sem necessidade de instalar SQL Server, MySQL ou docker.

## 2. Executar no Windows (mais simples)

Abra a pasta `LAB03S03_Completo` no PowerShell:

```powershell
.\iniciar_windows.ps1
```

O script cria `.venv`, instala dependências e inicia o servidor. Se o PowerShell bloquear scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar_windows.ps1
```

**Acesse** http://127.0.0.1:8000 (interface) ou http://127.0.0.1:8000/docs (API interativa).

## 3. Executar no Linux ou macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

O banco SQLite é criado na primeira execução. O pacote inclui um **banco fictício de demonstração**, sem dados reais, preparado para facilitar a avaliação.

## 4. Dados de demonstração

As credenciais são **somente para uso local**, jamais para hospedar publicamente.

| Perfil | Login | Senha |
|---|---|---|
| Professor | `professor@demo.local` | `Demo@12345` |
| Aluno | `aluno.demo` | `Demo@12345` |
| Empresa | `empresa.demo` | `Demo@12345` |

Caso o banco tenha sido removido, execute na raiz do projeto antes de iniciar a aplicação:

```bash
python -m scripts.preparar_demo
```

O script é idempotente: ele cadastra apenas contas/benefícios ainda inexistentes e aplica o crédito de demonstração do semestre `2026/2` **uma única vez**. A vantagem inicial é “Desconto no lanche”, com custo de 150 moedas.

## 5. Roteiro rápido de demonstração

1. Login como **professor**; veja as 1.000 moedas no painel. Selecione o aluno `Estudante Exemplo`, informe `200` moedas e motivo `Participação no projeto`, e confirme. Observe o extrato e o saldo de 800.
2. Saia e entre como **aluno**; confirme 200 moedas e o recebimento no extrato. Abra **Vantagens** e resgate `Desconto no lanche` por 150 moedas. Seu saldo será 50 e aparecerá o cupom.
3. Entre como **empresa**; confira suas vantagens no painel. Copie o código de cupom gerado para a área de conferência e execute a utilização. Tentar utilizar novamente é rejeitado.
4. Abra o banco `moeda_estudantil.db` com um cliente SQLite ou utilize os endpoints de consulta para mostrar que saldos, lançamentos, resgate, cupom e notificações estão persistidos.

**Atenção:** se já houve transferências/resgates no mesmo banco, os números do exemplo serão diferentes. Para uma demonstração reprodutível, use um banco novo e execute o seed antes do teste.

## 6. Créditos automáticos por semestre

O backend não oferece uma rota pública que permita a um professor criar moedas. A concessão pertence à rotina administrativa; execute manualmente na avaliação ou agende no início de cada semestre:

```bash
python -m scripts.creditar_semestre 2026/2
python -m scripts.creditar_semestre 2026/2
```

A segunda execução não realiza novo crédito. Troque para `2027/1` no semestre seguinte. Em produção, configure cron, Windows Task Scheduler, Azure Function ou outro agendador externo autorizado.

## 7. Envio de e-mails: fila persistente + SMTP

Transações e resgates sempre gravam **notificações `pendente`** no banco; não enviamos e-mails automaticamente dentro do request para evitar duplicidade em caso de falha da rede. Para entregar e-mails reais, configurar variáveis no `.env` (ver `.env.example`):

```dotenv
SMTP_HOST=smtp.exemplo.com
SMTP_PORT=587
SMTP_USER=usuario@exemplo.com
SMTP_PASSWORD=senha-de-aplicativo
SMTP_FROM=usuario@exemplo.com
SMTP_STARTTLS=1
```

Depois, executar:

```bash
python -m scripts.processar_notificacoes
```

**Sem SMTP configurado, nenhuma mensagem é enviada**: o script avisa e mantém os registros pendentes. Dados de demo usam domínios `.local`, portanto os endereços fictícios não recebem e-mail real. Para testar envio de verdade, atualize os e-mails cadastrados para caixas de teste autorizadas e configure uma conta SMTP própria. O sistema limita as tentativas por notificação a cinco.

## 8. Executar testes

```bash
python -m pytest -q
```

Foram verificados: criação e manutenção de cadastros, autenticação, privacidade, vínculo institucional, crédito idempotente, distribuição/rollback por saldo insuficiente, resgate, cupom único, autorização cruzada, desativação e fila de e-mail.

## 9. Estrutura do projeto

```text
LAB03S03_Completo/
├── app/
│   ├── main.py, config.py, database.py, models.py, schemas*.py, security.py
│   ├── routers/            # Controllers FastAPI
│   ├── services/           # Regras do domínio e transações
│   ├── repositories/       # Consultas dos CRUDs
│   ├── templates/          # Views Jinja2
│   └── static/             # CSS e JS
├── scripts/
│   ├── preparar_demo.py
│   ├── creditar_semestre.py
│   ├── processar_notificacoes.py
│   └── gerar_materiais_final.py
├── tests/                  # pytest
├── docs/
│   ├── LAB03S03_Relatorio_Completo.pdf
│   ├── ARQUITETURA_PERSISTENCIA.md
│   ├── API_SPRINT03.md
│   ├── RASTREABILIDADE_FINAL.md
│   ├── esquema_sqlite.sql
│   └── diagramas/          # ER, MVC, fluxo financeiro em formatos editáveis
├── apresentacao/
│   ├── LAB03S03_Apresentacao_Final_20min.pptx
│   ├── LAB03S03_Apresentacao_Final_20min.pdf
│   └── Roteiro_Apresentacao_20min.md
├── referencias/             # arquivos de origem e documentação da S02
├── moeda_estudantil.db      # banco de demonstração, fictício
├── iniciar_windows.ps1
├── requirements.txt
└── run.py
```

## 10. MVC e decisões técnicas

A camada **View** usa templates Jinja2 e `fetch` de JavaScript. Os **Controllers** são os módulos em `app/routers`; validam os dados de entrada com Pydantic e as permissões no servidor. O **Model** está em `app/models.py`, `app/services/` e schemas; operações de moedas usam SQL condicional e commit transacional. A **persistência** utiliza SQLAlchemy 2.x (ORM) e SQLite com checagem de FK e constraints. Detalhes e diagramas em `docs/ARQUITETURA_PERSISTENCIA.md`.

## 11. Limites importantes

O projeto é um **protótipo acadêmico**. Não inclui envio de e-mail já operacional sem SMTP, implantação pública, migrações Alembic, antifraude, fila distribuída, upload binário de fotos, tratamento LGPD completo, limitação de taxa e integração com instituição real. A chave de sessão padrão e contas demo **não são adequadas para produção**. Antes de qualquer hospedagem pública, revise os itens em `docs/ARQUITETURA_PERSISTENCIA.md`.

## 12. Documentos e apresentação

- Relatório de entrega: `docs/LAB03S03_Relatorio_Completo.pdf`.
- PPTX editável e slides PDF: `apresentacao/LAB03S03_Apresentacao_Final_20min.*`.
- Script de fala em 20 minutos: `apresentacao/Roteiro_Apresentacao_20min.md`.
- Modelo ER: `docs/diagramas/modelo_er.*` (mantido da S02).
- Diagrama de arquitetura: `docs/diagramas/arquitetura_final.*`.
- Fluxo de transações: `docs/diagramas/fluxo_transacoes.*`.
- API documentada: `docs/API_SPRINT03.md`, além do OpenAPI em `/docs`.

**Referência acadêmica:** `LABORATORIO_3_LAB_DESENVOLVIMENTO_DE_SOFTWARE`, seções 3 e 4.3; modelos e história da S01 e S02 fornecidos com o projeto.
