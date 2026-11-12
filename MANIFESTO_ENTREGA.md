# Manifesto — LAB04S02 | Implantação na nuvem

**Data:** novembro de 2026. **Disciplina:** Projeto de Software, PUC Minas. **Projeto:** Sistema de Moeda Estudantil (Mérito+), Release 2.

## Conformidade com o item 4.5 do enunciado

- [x] **Diagrama de Implantação** em UML: `docs/diagramas/implantacao.puml` (fonte) e `.png`, `.svg`, `.pdf`.
- [x] **Aplicação implantada na nuvem com Vercel e Render**: interface na Vercel (`frontend/`, `frontend/vercel.json`), API e PostgreSQL no Render (`render.yaml`). Endereços no `README.md`.
- [x] **Interface gráfica**: as telas do LAB03S03, agora publicadas como páginas estáticas que se comunicam com a API pelo proxy `/api` da Vercel.
- [x] **Modelos atualizados conforme o código**: arquitetura MVC (`docs/diagramas/arquitetura_lab04.*`), `docs/ARQUITETURA_PERSISTENCIA.md`, `docs/esquema_postgresql.sql`, rastreabilidade e API.
- [x] **Documentação para reproduzir o ambiente**: `docs/IMPLANTACAO.md` (passo a passo, variáveis, limites do plano gratuito, solução de problemas).
- [x] **Testes**: 61 testes automatizados (LAB03S03, LAB04S01 e LAB04S02) aprovados no SQLite e no PostgreSQL, além de verificação ponta a ponta com a API em modo produção.

## Principais artefatos para a avaliação

| Caminho | Conteúdo |
|---|---|
| `docs/IMPLANTACAO.md` | Como a aplicação foi implantada, por que e como reproduzir |
| `docs/diagramas/implantacao.*` | Diagrama de Implantação (UML) |
| `docs/diagramas/arquitetura_lab04.*` | Arquitetura MVC na nuvem |
| `render.yaml` | Infraestrutura do Render como código (API + PostgreSQL) |
| `frontend/vercel.json` | Configuração da Vercel: URLs, proxy `/api` e cabeçalhos de segurança |
| `app/tarefas.py`, `app/services/notificacoes.py` | Crédito semestral e fila de e-mails automáticos no servidor (desde o LAB04S01; dispensam agendador pago) |
| `tests/test_implantacao.py` | Testes da implantação e do alinhamento interface × API |

## Premissas e limitações declaradas

- Planos gratuitos: a API "dorme" após um período sem acessos (o primeiro acesso leva cerca de 1 minuto) e o PostgreSQL gratuito do Render expira 30 dias após a criação.
- Segredos (`SECRET_KEY`, `DEMO_SENHA`, `SMTP_*`) ficam apenas no painel do Render; nada sensível está no repositório ou neste pacote.
- Sem `SMTP_*` configurado, as notificações permanecem pendentes no banco, como no LAB03S03.

**Histórico:** os manifestos anteriores estão em `referencias/LAB04S01_historico/` e `referencias/LAB03S03_historico/`.
