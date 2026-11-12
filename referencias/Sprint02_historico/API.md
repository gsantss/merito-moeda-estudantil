# API HTTP — Sistema de Moeda Estudantil (Sprint 02)

**Base local:** `http://127.0.0.1:8000` · **Formato:** `application/json` · **Swagger:** `/docs`.

## Controle de sessão e CSRF

A API usa sessão assinada em cookie HTTPOnly. Antes de qualquer operação de escrita, a página faz `GET /api/sessao`, recebe `csrf_token` e envia esse valor como `X-CSRF-Token`. O token é rotacionado quando o login é bem-sucedido. As rotas POST/PUT/DELETE retornam 403 sem token correspondente.

| Verbo | Rota | Segurança | Operação |
|---|---|---|---|
| GET | `/api/sessao` | Pública | Informações da sessão + token CSRF |
| POST | `/api/auth/login` | CSRF | Login e senha, inicia sessão |
| POST | `/api/auth/logout` | CSRF | Encerra sessão |
| GET | `/api/instituicoes` | Pública | Lista instituições ativas |
| GET | `/api/carteira` | Autenticado | Saldo atual, ou `null` se empresa |
| POST | `/api/alunos` | CSRF | Cadastro de aluno |
| GET | `/api/alunos` | Aluno / Professor | Aluno vê apenas seu perfil; professor vê alunos da instituição (sem CPF/e-mail) |
| GET | `/api/alunos/{id}` | Dono ou professor da instituição | Detalhes restritos conforme perfil |
| PUT | `/api/alunos/{id}` | Dono + CSRF | Atualização de aluno (CPF e login imutáveis nesta sprint) |
| DELETE | `/api/alunos/{id}` | Dono + CSRF | Exclusão se sem saldo/transações/resgates |
| POST | `/api/empresas` | CSRF | Cadastro de empresa |
| GET | `/api/empresas` | Pública | Lista nome e descrição dos parceiros |
| GET | `/api/empresas/{id}` | Pública/dono | Perfil público; dono também recebe dados de contato e login |
| PUT | `/api/empresas/{id}` | Dono + CSRF | Atualização da empresa |
| DELETE | `/api/empresas/{id}` | Dono + CSRF | Exclusão se sem vantagens cadastradas |

## Payloads

### Aluno — POST `/api/alunos`

```json
{
  "nome": "Maria Silva",
  "email": "maria@example.com",
  "cpf": "52998224725",
  "rg": "MG123456",
  "endereco": "Rua Exemplo, 10, Belo Horizonte",
  "curso": "Engenharia de Software",
  "instituicao_id": "UUID obtido via GET /api/instituicoes",
  "login": "maria",
  "senha": "SenhaSegura123"
}
```

A criação gera usuário autenticável, perfil `alunos` e carteira de saldo 0 em uma única transação. O `PUT` espera `nome`, `email`, `rg`, `endereco`, `curso`, `instituicao_id` e aceita `senha_nova` opcional; não atualiza CPF/login. Para trocar de instituição, selecionar uma instituição ativa.

### Empresa — POST `/api/empresas`

```json
{
  "nome": "Restaurante Universitário",
  "email_contato": "restaurante@example.com",
  "cnpj": null,
  "descricao": "Descontos para alunos",
  "login": "restaurante",
  "senha": "SenhaSegura123"
}
```

O `PUT` espera `nome`, `email_contato`, `cnpj` (pode ser `null`), `descricao` (pode ser `null`) e aceita `senha_nova` opcional. O CNPJ é opcional; quando informado, é validado. O cadastro não possui carteira financeira nesta etapa.

### Login — POST `/api/auth/login`

```json
{"login": "maria", "senha": "SenhaSegura123"}
```

## Códigos HTTP

- `200`: operação bem-sucedida (leitura, atualização, exclusão, login).
- `201`: novo cadastro criado.
- `401`: sessão não autenticada ou credenciais inválidas.
- `403`: perfil sem permissão, acesso a dados alheios ou token CSRF inválido.
- `404`: entidade não encontrada.
- `409`: conflito de unicidade ou exclusão bloqueada por histórico/vínculos.
- `422`: payload inválido, incluindo campos obrigatórios, CPF/CNPJ, instituição ausente.

## Observações de escopo

Endpoints para envio de moedas, crédito semestral, catálogo de vantagens, resgates, emissão de cupons ou envio de e-mails **não existem nesta sprint**. Tabelas destinadas a essas ações foram previstas no esquema, conforme a modelagem e o enunciado.
