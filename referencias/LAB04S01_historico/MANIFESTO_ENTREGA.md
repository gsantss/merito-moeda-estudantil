# Manifesto — LAB04S01 | Diagramas de interação e casos de uso restantes

**Data:** novembro de 2026. **Disciplina:** Projeto de Software, PUC Minas. **Projeto:** Sistema de Moeda Estudantil (Mérito+), Release 2.

## Conformidade com o item 4.4 do enunciado

- [x] **Diagramas de Sequência (UML)**: 10 diagramas, um por caso de uso do catálogo da LAB03S01 (UC01 a UC09 e UC12; UC10, UC11 e UC13 aparecem incluídos em SD04 e SD09). Fontes em `docs/diagramas/sequencia/*.puml`, com PNG e SVG.
- [x] **Diagrama de Visão Geral de Interação (UML)**: `docs/diagramas/visao_geral_interacao.*`, com usos de interação (`ref`) para cada diagrama de sequência.
- [x] **Casos de uso restantes implementados**: UC05 (crédito semestral pelo agendador) e UC12 (envio de e-mails), que no LAB03S03 dependiam de um operador, agora rodam automaticamente no servidor (`app/tarefas.py`, `app/services/notificacoes.py`).
- [x] **Alinhamento modelo × código**: `tests/test_diagramas_interacao.py` verifica que cada função e rota dos diagramas de sequência existe no código.
- [x] **Testes**: 36 testes automatizados aprovados (11 do LAB03S03 e 25 novos).

## Principais artefatos para a avaliação

| Caminho | Conteúdo |
|---|---|
| `docs/LAB04S01_DIAGRAMAS_INTERACAO.md` | Guia da entrega: casos de uso restantes, mapa caso de uso → diagrama → código |
| `docs/diagramas/sequencia/` | Diagramas de sequência SD01 a SD10 |
| `docs/diagramas/visao_geral_interacao.*` | Diagrama de visão geral de interação |
| `app/tarefas.py` | Agendador do servidor: crédito semestral (UC05) e envio da fila (UC12) |
| `app/services/notificacoes.py` | Envio SMTP da fila de notificações, atrás da interface `EnviadorEmail` |
| `tests/test_lab04s01.py`, `tests/test_diagramas_interacao.py` | Testes desta entrega |
| `docs/RASTREABILIDADE_FINAL.md` | Histórias HU01 a HU16 com evidências e diagramas de sequência |

## Premissas e limitações declaradas

- Sem SMTP configurado, as notificações continuam pendentes no banco (comportamento mantido do LAB03S03).
- O semestre é definido pelo calendário civil: janeiro a junho (`AAAA/1`) e julho a dezembro (`AAAA/2`).
- As regras de negócio, os modelos e as telas do LAB03S03 não foram alterados.

**Histórico:** o manifesto da entrega anterior está em `referencias/LAB03S03_historico/MANIFESTO_ENTREGA.md`.
