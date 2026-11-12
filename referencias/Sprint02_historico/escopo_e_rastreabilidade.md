# LAB03S02 — Escopo, decisões e rastreabilidade

## Contexto

O enunciado, seção 4.2, solicita três grupos de entregas: (1) Modelo Entidade-Relacionamento; (2) definição e implementação da estratégia de acesso ao banco de dados — ORM/DAO, etc.; (3) CRUDs iniciais de aluno e empresa parceira, com front-end comunicando com o back-end.

O relatório LAB03S01, seção 1.2, prevê exatamente essa transição da Sprint 01 para a Sprint 02. Esta implementação mantém o vocabulário de negócio, as responsabilidades e as multiplicidades das figuras do Anexo B (diagrama de classes) e Anexo C (diagrama MVC).

## Mapeamento de requisitos

| Origem LAB03S01 | Requisito/modelagem | Concretização LAB03S02 | Situação |
|---|---|---|---|
| UC01 / HU01 / RN01 | Cadastro de aluno e instituição pré-cadastrada | Formulário, API, validação e FK `instituicao_id` | Funcional |
| UC06 / HU04 | Cadastro de empresa parceira | Formulário, API e perfil de empresa | Funcional |
| UC02 / HU02 / HU16 / RN12 | Autenticação/roles | Sessão, hash PBKDF2, validação no servidor | Funcional |
| HU03 / RN02 | Professor pré-cadastrado/vinculado | Seed local com instituição e departamento | Demonstração |
| UC03 / HU09 / HU10 / RN08 | Saldo e extrato | Carteira inicial e contrato de saldo; tabela de transações | Parcial: sem extrato |
| UC05 / HU05 / RN03 / RN04 | 1.000 moedas por semestre, idempotência | `creditos_semestrais` com UNIQUE professor+semestre | Esquema preparado |
| UC04 / HU06 / HU07 / RN05 / RN06 | Distribuir moedas com saldo e motivo | Carteira e tabela de transações | Esquema preparado |
| UC12 / HU08 / RN07 | Notificar aluno sem duplicar transação | `notificacoes` com status/tentativas | Esquema preparado |
| UC07 / HU11 / RN09 | Vantagens da empresa | Tabela `vantagens` e relacionamento FK | Esquema preparado |
| UC08 / HU12 | Catálogo de vantagens | Não implementado na Sprint 02 | Sprint 03 |
| UC09 / HU13 / RN10 | Resgate com débito | `resgates` associado à transação | Esquema preparado |
| UC11 / HU14 / RN11 | Cupom único e notificação | `cupons` com UNIQUE código e resgate | Esquema preparado |
| UC10 / HU15 | Integridade financeira | CHECKs e FK; transação no cadastro/CRUD | Regras financeiras na Sprint 03 |
| Diagrama de classes, Anexo B | Herança/associações | `usuarios` + tabelas de perfil; FKs 1:N e 1:1 | Modelo ER |
| Diagrama MVC, Anexo C | Separação View/Controller/Model/persistência | Templates + rotas FastAPI + services + repositories ORM | Funcional |

## Decisões de projeto

**D01 — Linguagem/framework:** Python 3.11+, FastAPI, Jinja2, JavaScript moderno (Fetch API), SQLAlchemy 2 e SQLite. Os modelos da Sprint 01 não impõem framework nem SGBD.

**D02 — Herança UML:** o usuário abstrato não vira uma classe SQL isolada; usa-se tabela concreta de autenticação `usuarios` e subtipos `alunos`, `professores` e `empresas_parceiras` com chave primária também chave estrangeira. A associação é 1:0..1 e o campo `perfil` define o subtipo, exigido nos serviços.

**D03 — Empresa:** seguindo premissa A02 do relatório anterior, nome e e-mail de contato são obrigatórios; descrição e CNPJ são complementares e opcionais. Os dados não obrigatórios extrapolam minimamente o modelo para uso operacional.

**D04 — Instituições/professores:** instituições e professor foram criados via seed local para demonstração, não por cadastro público, preservando RN01/RN02. O professor possui login conhecido de teste (premissa A03), que deve ser substituído em produção.

**D05 — Saldo:** aluno recebe carteira de saldo 0 no cadastro; empresa não recebe carteira. Creditagem semestral e envio de moedas são regras de outra sprint.

**D06 — Exclusão:** para futura integridade de auditoria, usuário/aluno com saldo ou transações e empresa com vantagens não podem ser removidos diretamente (HTTP 409). Exclusão de um cadastro recém-criado, sem vínculos, está funcional.

**D07 — Unicidade/idempotência:** `creditos_semestrais(professor_id, semestre)` único e `cupons(codigo)` único; negócio a ser implementado na Sprint 03.

**D08 — Segurança acadêmica:** senha com hash PBKDF2 e salt, cookie assinado HTTPOnly, SameSite=Lax, CSRF em mutações e verificação de autorização no servidor. Validação de CPF/CNPJ, unicidade e restrições de domínio. Banco SQLite voltado a uso local.

## Matriz de entrega LAB03S02

1. **Modelo ER:** `docs/diagramas/modelo_er.svg`, `.puml`, `.mmd`, `.png`, `.pdf`.
2. **Esquema físico:** `app/models.py` e `docs/esquema_sqlite.sql`.
3. **Estratégia de persistência:** `app/database.py`, `app/repositories/`, `app/services/`.
4. **CRUD e comunicação front/back:** `app/routers/alunos.py`, `empresas.py`, templates e `app/static/js/app.js`.
5. **Documentação:** README, API e relatório PDF.
6. **Validação:** testes Pytest com banco temporário.

## Limites declarados

Não há envio real de e-mail, crédito de 1.000 moedas, distribuição monetária, cadastro funcional de vantagem, consulta de extrato, resgate, cupom utilizável ou tutorial tecnológico nesta entrega. Não afirmar estes itens como desenvolvidos. São elementos de modelagem/preparação para completar na LAB03S03.
