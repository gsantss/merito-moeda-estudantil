# Manifesto — LAB03S03 | Entrega final

**Data:** outubro de 2026. **Disciplina:** Projeto de Software, PUC Minas. **Projeto:** Sistema de Moeda Estudantil.

## Conformidade com o item 4.3 do enunciado

- [x] CRUD **final** de Aluno com telas de cadastro e painel de consulta/edição/exclusão ou desativação, API e validações.
- [x] CRUD **final** de Empresa Parceira com telas de cadastro e painel de consulta/edição/exclusão ou desativação, API e validações.
- [x] Apresentação da arquitetura MVC: código-fonte, diagrama atualizado, relatório e slides.
- [x] Apresentação da persistência: 12 tabelas, ER atualizado da S02, ORM, SQL físico, constraints e transações.
- [x] Protótipo final funcional cobrindo saldo, extrato, 1.000 moedas semestrais, distribuição, vantagens, resgate, cupom e autorização.
- [x] Tutorial das tecnologias escolhidas e apresentação com aproximadamente 20 minutos.
- [x] Testes automatizados: 11 cenários aprovados.

## Principais artefatos para a avaliação

| Caminho | Conteúdo |
|---|---|
| `docs/LAB03S03_Relatorio_Completo.pdf` | Relatório acadêmico (8 páginas) |
| `apresentacao/LAB03S03_Apresentacao_Final_20min.pptx` | Apresentação editável de 20 slides |
| `apresentacao/LAB03S03_Apresentacao_Final_20min.pdf` | Versão PDF dos slides |
| `apresentacao/Roteiro_Apresentacao_20min.md` | Roteiro oral, com tempo e perguntas prováveis |
| `docs/ARQUITETURA_PERSISTENCIA.md` | Descrição técnica completa de MVC, ORM e integridade |
| `docs/diagramas/` | Modelos ER, arquitetura e fluxo de transações, com fontes editáveis |
| `docs/API_SPRINT03.md` | Especificação das rotas e permissões |
| `docs/RASTREABILIDADE_FINAL.md` | Cobertura HU01–HU16 |
| `app/` | Código do protótipo com View/Controller/Model |
| `tests/` | Testes reexecutáveis com pytest |
| `scripts/` | Demo, crédito semestral, notificações e gerador de materiais |
| `moeda_estudantil.db` | Dados **fictícios** da demonstração local |
| `README.md` | Instalação, execução, testes, contas e limitações |

## Premissas e limitações declaradas

- Sem configurações SMTP reais, mensagens permanecem na fila, sem afirmar envio real.
- Crédito semestral é responsabilidade de um job do operador; `python -m scripts.creditar_semestre AAAA/S`.
- Contas com registros financeiros e vantagens com resgates são desativadas, não apagadas fisicamente.
- O banco SQLite e credenciais predefinidas são apenas para demonstrar localmente, não para produção.
- A estrutura de pastas não inclui `.venv`, `__pycache__` ou caches; dependências se instalam por requirements.

**Referências originais:** documentos do usuário sob `referencias/` e relatório S02 preservado em `referencias/Sprint02_historico/`.
