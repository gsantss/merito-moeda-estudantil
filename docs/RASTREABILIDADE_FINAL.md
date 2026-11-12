# Matriz de rastreabilidade — S01 → S03

Rastreia as 16 histórias do documento `LAB03S01_Relatorio_Completo.pdf` até evidências do protótipo final.

| História | Realização | Evidência principal |
| --- | --- | --- |
| HU01 | Cadastro de aluno, instituição validada | `POST /api/alunos` · `test_aluno_criar_ler_editar_excluir` |
| HU02 | Login e permissão por perfil | `/api/auth/login` · `test_perfis_nao_alteram_contas_alheias` |
| HU03 | Professor pré-cadastrado com instituição | `app/seed.py`, `app/models.py` |
| HU04 | Empresa parceira com autenticação | `POST /api/empresas` · `test_empresa_criar_ler_editar_excluir` |
| HU05 | Crédito semestral acumulativo e idempotente | Automático no servidor: `app/tarefas.py` (LAB04S01); manual: `scripts/creditar_semestre.py` · `test_credito_semestral_idempotente_e_acumulativo`, `test_agendador_credita_o_semestre_atual_uma_unica_vez` |
| HU06 | Distribuição com quantidade e motivo | `POST /api/distribuicoes`, `test_transferencia_integral_restricoes_e_notificacao` |
| HU07 | Saldo insuficiente bloqueado e rollback | `_debitar()` em `app/services/financeiro.py` |
| HU08 | Notificação sobre moedas recebidas | Fila `notificacoes` enviada automaticamente por `app/services/notificacoes.py` (LAB04S01) · `test_fila_de_notificacoes_envia_e_repete_falhas_ate_o_limite` |
| HU09 | Saldo e extrato do professor | `GET /api/extrato` · painel |
| HU10 | Saldo e extrato do aluno | `GET /api/extrato` · painel |
| HU11 | Vantagem com custo, descrição e foto | `/api/vantagens` · `test_segurança_cruzada_e_edicao_vantagem` |
| HU12 | Catálogo de vantagens ativas | `GET /api/vantagens` · `/vantagens` |
| HU13 | Resgate com saldo suficiente | `POST /api/resgates` · `test_vantagens_resgates_cupom_unico_empresa_e_saldo` |
| HU14 | Cupom único nos dois e-mails | `cupons` e duas `notificacoes` por resgate |
| HU15 | Integridade de transações | Transações ACID, constraints SQL e testes do financeiro |
| HU16 | Ações sensíveis restritas | `exigir_csrf()`, `exigir_dono()`, `exigir_perfil()` |

**Observação (LAB03S03):** as mensagens de e-mail eram criadas na fila de persistência, mas o envio real dependia de uma conta SMTP externa e da execução manual do processador.

**Atualização (LAB04S01):** o envio passou a ser feito automaticamente pelo servidor a cada 60 segundos, desde que haja SMTP configurado. Sem SMTP, as mensagens continuam pendentes no banco.

## Diagramas de sequência por história (LAB04S01)

| Diagrama | Histórias |
| --- | --- |
| SD01 Cadastrar aluno | HU01 |
| SD02 Autenticar usuário | HU02, HU03, HU16 |
| SD03 Consultar saldo e extrato | HU09, HU10 |
| SD04 Distribuir moedas | HU06, HU07, HU15, HU16 |
| SD05 Creditar moedas semestrais | HU05 |
| SD06 Cadastrar empresa parceira | HU04 |
| SD07 Cadastrar vantagem | HU11, HU16 |
| SD08 Consultar vantagens | HU12 |
| SD09 Resgatar vantagem | HU13, HU14, HU15, HU16 |
| SD10 Enviar notificações por e-mail | HU08, HU14 |

Fontes em `docs/diagramas/sequencia/`; guia em `docs/LAB04S01_DIAGRAMAS_INTERACAO.md`.
