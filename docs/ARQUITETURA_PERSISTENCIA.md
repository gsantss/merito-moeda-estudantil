# Arquitetura MVC, dados e persistência — LAB03S03

## Alinhamento com a Sprint 01

O Anexo C da S01 separa **View / Controller / Model / Infraestrutura**. A S02 implementou a base com FastAPI, SQLAlchemy e SQLite. A S03 mantém a mesma estrutura e completa os fluxos de carteira, vantagens e resgates. Os diagramas finais estão em `docs/diagramas/arquitetura_final.{png,svg,pdf,dot}` e `fluxo_transacoes.{png,svg,pdf,dot}`.

| Camada MVC | Componentes no repositório | Responsabilidade |
| --- | --- | --- |
| View | `app/templates/`, `app/static/js/`, `app/static/css/` | Telas responsivas e formulários; chamadas `fetch` com sessão e CSRF |
| Controller | `app/routers/` | Rotas HTTP, perfis, autenticação, DTO de entrada, respostas e status |
| Model / Services | `app/models.py`, `app/schemas*.py`, `app/services/` | Entidades, validação de CPF/CNPJ, saldos, débitos, cupons e regras de negócio |
| Acesso a dados | `app/repositories/`, `app/database.py`, SQLAlchemy ORM | Consultas com `select()`, operações condicionais com `update()`, commit/rollback |
| Infraestrutura | SQLite, `scripts/creditar_semestre.py`, `scripts/processar_notificacoes.py` | Persistência ACID, agendamento externo e saída SMTP |

## Modelo Entidade-Relacionamento

O modelo ER da S02 permanece válido, com 12 tabelas, pois a S02 já antecipou os dados necessários às funcionalidades da S03: `instituicoes`, `usuarios`, `alunos`, `professores`, `empresas_parceiras`, `carteiras`, `transacoes_moedas`, `creditos_semestrais`, `vantagens`, `resgates`, `cupons` e `notificacoes`. Veja `docs/diagramas/modelo_er.pdf` e `docs/esquema_sqlite.sql`.

O relacionamento de usuário para perfil é 1:0..1 e determinado pelo campo `perfil`; alunos/professores possuem 1 carteira; empresas têm 0..* vantagens; cada resgate pertence a 1 aluno, 1 vantagem e gera 1 cupom; cada transação financeira é persistida no extrato. Há unicidade por CPF, login, e-mail e código de cupom, e por par `(professor_id, semestre)`.

## Consistência e transações

1. A distribuição debita a carteira do professor com `UPDATE ... WHERE saldo >= valor`, credita a carteira do aluno e grava transação e e-mail pendente **no mesmo commit**. Se uma etapa falha, ocorre rollback.
2. O resgate debita a carteira do aluno com a mesma guarda, grava transação, resgate, cupom aleatório único e dois registros de notificação em um commit.
3. O crédito semestral grava vínculo de unicidade do professor com semestre; reexecutar o job não duplica o crédito. O semestre é informado pelo agendador externo (`AAAA/1` ou `AAAA/2`), pois a data institucional não foi especificada.
4. O envio SMTP ocorre **fora** da transação financeira, via script. A ausência de SMTP mantém a notificação `pendente`; o sistema não a marca como enviada. O operador pode reagendar falhas com até 5 tentativas.
5. Não se pode apagar movimentações já efetuadas. Contas com histórico são desativadas e vantagens que tiveram resgates são desativadas em vez de eliminadas, preservando auditoria.

## Estratégia de persistência

- SGBD: SQLite para executar localmente e demonstrar sem dependência externa; ORM: SQLAlchemy 2.x.
- `Base.metadata.create_all()` para inicializar banco vazio; não substitui migrações em ambiente produtivo.
- Chaves primárias UUID string, `ForeignKey` e `CheckConstraint`, além de unicidade no banco.
- `PRAGMA foreign_keys=ON` por conexão, `busy_timeout` para espera de bloqueio, e `Session` por requisição.
- Senhas em PBKDF2-SHA256 com salt, cookie assinado HTTPOnly, token anti-CSRF e checagem de RBAC no backend.
- O banco local de demonstração não representa um serviço pronto para produção. Não há migration de dados de produção, monitoramento centralizado, provedor real configurado ou implantação em nuvem.

## Operação e segurança

Antes de publicar, definir `SECRET_KEY` próprio e `SESSION_HTTPS_ONLY=1`, ativar TLS, atualizar configurações SMTP, adicionar rate limiting, recuperação de senha e políticas de consentimento/privacidade. O usuário possui autorização para seus próprios cadastros; o professor visualiza apenas alunos de sua instituição e o parceiro somente suas vantagens e cupons.
