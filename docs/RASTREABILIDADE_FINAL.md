# Matriz de rastreabilidade — S01 → S03

Rastreia as 16 histórias do documento `LAB03S01_Relatorio_Completo.pdf` até evidências do protótipo final.

| História | Realização | Evidência principal |
| --- | --- | --- |
| HU01 | Cadastro de aluno, instituição validada | `POST /api/alunos` · `test_aluno_criar_ler_editar_excluir` |
| HU02 | Login e permissão por perfil | `/api/auth/login` · `test_perfis_nao_alteram_contas_alheias` |
| HU03 | Professor pré-cadastrado com instituição | `app/seed.py`, `app/models.py` |
| HU04 | Empresa parceira com autenticação | `POST /api/empresas` · `test_empresa_criar_ler_editar_excluir` |
| HU05 | Crédito semestral acumulativo e idempotente | `scripts/creditar_semestre.py`, `test_credito_semestral_idempotente_e_acumulativo` |
| HU06 | Distribuição com quantidade e motivo | `POST /api/distribuicoes`, `test_transferencia_integral_restricoes_e_notificacao` |
| HU07 | Saldo insuficiente bloqueado e rollback | `_debitar()` em `app/services/financeiro.py` |
| HU08 | Notificação sobre moedas recebidas | `notificacoes` e `scripts/processar_notificacoes.py` |
| HU09 | Saldo e extrato do professor | `GET /api/extrato` · painel |
| HU10 | Saldo e extrato do aluno | `GET /api/extrato` · painel |
| HU11 | Vantagem com custo, descrição e foto | `/api/vantagens` · `test_segurança_cruzada_e_edicao_vantagem` |
| HU12 | Catálogo de vantagens ativas | `GET /api/vantagens` · `/vantagens` |
| HU13 | Resgate com saldo suficiente | `POST /api/resgates` · `test_vantagens_resgates_cupom_unico_empresa_e_saldo` |
| HU14 | Cupom único nos dois e-mails | `cupons` e duas `notificacoes` por resgate |
| HU15 | Integridade de transações | Transações ACID, constraints SQL e testes do financeiro |
| HU16 | Ações sensíveis restritas | `exigir_csrf()`, `exigir_dono()`, `exigir_perfil()` |

**Observação:** as mensagens de e-mail são criadas corretamente na fila de persistência, mas o envio real depende de uma conta SMTP externa configurada e da execução do processador. Essa diferença é explícita no README e no relatório.
