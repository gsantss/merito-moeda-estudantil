# Diagramas

Todas as versões dos modelos ficam no repositório, como pede o enunciado. Fontes editáveis (`.puml`, `.dot`, `.mmd`) e exportações (`.png`, `.svg`, `.pdf`).

| Diagrama | Arquivos | Versão |
| --- | --- | --- |
| **Sequência (10 diagramas, um por caso de uso)** | `sequencia/sd01…sd10_*.puml` · `.png` · `.svg` | **LAB04S01** |
| **Visão geral de interação** | `visao_geral_interacao.puml` · `.png` · `.svg` · `.pdf` | **LAB04S01** |
| Arquitetura MVC final | `arquitetura_final.dot` · `.png` · `.svg` · `.pdf` | LAB03S03 |
| Fluxo das transações | `fluxo_transacoes.dot` · `.png` · `.svg` · `.pdf` | LAB03S03 |
| Modelo ER | `modelo_er.puml` · `.mmd` · `.dot` · `.png` · `.svg` · `.pdf` | LAB03S02 (continua válido: 12 tabelas) |
| Arquitetura MVC inicial | `arquitetura_mvc.puml` | LAB03S02 |

Os diagramas de sequência são verificados contra o código por `tests/test_diagramas_interacao.py` (veja `docs/LAB04S01_DIAGRAMAS_INTERACAO.md`).

O código SQLAlchemy em `app/models.py` é a fonte de verdade da estrutura física; `docs/esquema_sqlite.sql` contém o DDL gerado a partir desse código.
