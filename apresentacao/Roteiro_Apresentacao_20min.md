# Roteiro para apresentação final LAB03S03 (20 minutos)

**Material de apoio:** `LAB03S03_Apresentacao_Final_20min.pptx` (20 slides). Abra a aplicação e deixe as três contas de demonstração preparadas antes de começar.

## 00:00 – 02:30 · Introdução e evolução (slides 1–4)

Apresente o problema: como reconhecer o esforço e a participação de alunos com moeda virtual? Professores recompensam, alunos acumulam e empresas oferecem vantagens. Explique as três fases: S01 definiu casos de uso, histórias e diagramas; S02 colocou o banco, o acesso com ORM e o CRUD inicial; S03 concluiu o CRUD, ampliou os fluxos e incorporou a arquitetura final em execução.

**Fala-chave:** “Nós procuramos preservar os modelos já entregues e converter cada regra de negócio em comportamento observável, sem reescrever o projeto do zero.”

## 02:30 – 06:20 · Arquitetura e tutorial das tecnologias (slides 5–8)

Abra o diagrama MVC. Mostre que a interface Jinja2/JS envia requisições HTTP ao FastAPI. Controllers lidam com autenticação, entrada e autorização. Serviços aplicam as regras. SQLAlchemy mapeia as entidades e controla a transação sobre SQLite.

Demonstre o caminho de uma rota: `app/routers/financeiro.py` recebe `/api/distribuicoes`; `app/services/financeiro.py` verifica saldo, realiza os dois lançamentos e grava a notificação; o SQLAlchemy salva no banco. Explique o motivo do ORM: associação de classes às tabelas, consultas legíveis e independência parcial da sintaxe SQL.

## 06:20 – 10:20 · Regras e CRUDs finais (slides 9–14)

Mostre o painel do aluno e o da empresa, com consulta, alteração, exclusão ou desativação segura. Mostre a regra de 1.000 moedas a cada semestre e por que não existe rota pública para criar crédito. Explique a validação de saldo antes de qualquer débito e o registro atômico. No resgate, um cupom único é persistido, e duas notificações são gravadas na fila, uma para cada destinatário.

**Fala-chave:** “Um e-mail falhar não pode fazer o aluno receber moedas duplicadas; por isso o envio está desacoplado da transação financeira.”

## 10:20 – 12:20 · Segurança e qualidade (slides 15–16)

Cite PBKDF2, cookies HTTPOnly, CSRF e permissão no backend. Demonstre `python -m pytest -q` e explique os casos: créditos idempotentes, saldo insuficiente, acesso a dados de outro perfil e reutilização de cupom. Os testes aprovados são evidências do protótipo, não certificação de segurança de produção.

## 12:20 – 18:30 · Demonstração e tutorial prático (slides 17–18, navegação ao vivo)

1. Abra `/painel` como `professor@demo.local / Demo@12345`. Selecione `Estudante Exemplo`, informe `200` moedas e um motivo, e pressione Enviar. Confira o extrato. (~2 min)
2. Saia e entre com `aluno.demo / Demo@12345`. Mostre o crédito e o extrato. Acesse `/vantagens` e resgate `Desconto no lanche` de 150 moedas; copie o cupom criado. (~2 min)
3. Saia e entre com `empresa.demo / Demo@12345`. Mostre o gerenciamento de vantagens, cole o cupom e realize a baixa; explique que uma segunda baixa será rejeitada. (~1,5 min)
4. Mostre `/docs` ou o SQLite para comprovar a persistência. Caso o SMTP não esteja configurado, explique que as notificações permanecem pendentes; não anuncie envio real. (~0,5 min)

## 18:30 – 20:00 · Limitações e encerramento (slides 19–20)

Explique que o SQLite, o seed e as senhas de demo são para execução local, enquanto um ambiente de produção precisaria de HTTPS, segredos próprios, infraestrutura SMTP e agendamento de semestre. Termine retomando o principal resultado: o mesmo modelo e a mesma arquitetura fundamentam um sistema demonstrável com os fluxos principais de ponta a ponta. Perguntas.

## Perguntas prováveis da professora

**Por que SQLAlchemy e não SQL manual?** Pelo mapeamento entre modelos e tabelas, consultas parametrizadas e transações coerentes; constraints SQL continuam no banco.

**Como evita professor gastar mais moedas do que tem?** O débito usa `UPDATE ... WHERE saldo >= quantidade`, validando a alteração de uma única linha; se não altera, responde HTTP 409 e ocorre rollback.

**Como evita duplicar 1.000 moedas?** Restrição única `(professor_id, semestre)`, verificação antes e handling de conflito em transação.

**Por que e-mails não saem imediatamente?** A transação financeira persiste primeiro; um processador independente lê as mensagens pendentes e tenta SMTP. Falhas de e-mail não repetem moedas.

**Por que não apagar aluno com extrato?** A integridade histórica exige manter as transações. O sistema oferece desativação de conta preservando o histórico.

**O que mudou da S02?** Novos serviços, rotas, telas, testes e regras financeiras, mantendo ORM e 12 tabelas do ER já previsto.
