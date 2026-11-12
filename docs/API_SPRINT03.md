# API da Sprint 03 — HTTP e permissões

Documentação interativa em `http://127.0.0.1:8000/docs`. Todas as rotas de escrita exigem cabeçalho `X-CSRF-Token`, emitido em `GET /api/sessao`. O cookie de sessão (`moeda_session`) é enviado automaticamente pelo navegador.

| Método | Endpoint | Permissão | Resultado |
| --- | --- | --- | --- |
| GET | `/api/sessao` | Pública | Sessão e CSRF |
| POST | `/api/auth/login` | Pública + CSRF | Sessão do perfil |
| POST | `/api/auth/logout` | Sessão + CSRF | Encerrar sessão |
| GET | `/api/instituicoes` | Pública | Instituições ativas |
| POST / GET / PUT / DELETE | `/api/alunos[/{id}]` | Criação pública; leitura própria/professor; alteração/exclusão do próprio aluno | CRUD final do aluno |
| PATCH | `/api/alunos/{id}/desativar` | Aluno titular | Desativação quando há histórico |
| POST / GET / PUT / DELETE | `/api/empresas[/{id}]` | Criação pública; consulta pública limitada; alteração/exclusão da titular | CRUD final da empresa |
| PATCH | `/api/empresas/{id}/desativar` | Empresa titular | Desativação e retirada das vantagens do catálogo |
| GET | `/api/carteira` | Sessão | Saldo atual, se existe carteira |
| GET | `/api/extrato` | Aluno / Professor | Saldo e movimentações próprias |
| GET | `/api/vantagens` | Pública | Catálogo ativo |
| GET | `/api/vantagens/minhas` | Empresa | Vantagens próprias (inclusive inativas) |
| POST | `/api/vantagens` | Empresa + CSRF | Criar vantagem |
| PUT / DELETE | `/api/vantagens/{id}` | Empresa titular + CSRF | Atualizar / desativar |
| POST | `/api/distribuicoes` | Professor + CSRF | Debitar, creditar, registrar e enfileirar notificação |
| POST | `/api/resgates` | Aluno + CSRF | Debitar e emitir cupom único |
| GET | `/api/cupons` | Aluno | Cupons próprios |
| GET | `/api/cupons/conferir/{codigo}` | Empresa titular | Conferir cupom sem consumir |
| POST | `/api/cupons/utilizar` | Empresa titular + CSRF | Baixa presencial única |

## Exemplos de requisições

### Vantagem

```json
{"titulo":"Desconto na cantina","descricao":"Desconto em um lanche no campus","foto_url":"https://example.org/foto.jpg","custo":150,"ativa":true}
```

### Distribuição

```json
{"aluno_id":"UUID_DO_ALUNO","quantidade":200,"motivo":"Participação nas atividades"}
```

### Resgate

```json
{"vantagem_id":"UUID_DA_VANTAGEM"}
```

### Cupom presencial

```json
{"codigo":"MER-0123456789ABCDEF"}
```

Respostas de erro: `401` não autenticado, `403` perfil incorreto, `404` inexistente/sem acesso, `409` conflito/saldo insuficiente e `422` validação de entrada.
