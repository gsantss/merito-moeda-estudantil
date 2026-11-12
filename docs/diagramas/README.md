# Diagramas — LAB03S02

- `modelo_er.puml`: fonte PlantUML do Modelo Entidade-Relacionamento (modelo físico/lógico detalhado).
- `modelo_er.mmd`: versão Mermaid do Modelo ER, visualizável no GitHub.
- `modelo_er.dot`: fonte Graphviz do desenho exportado.
- `modelo_er.svg` e `modelo_er.png`: visualizações exportadas do esquema SQLAlchemy.
- `arquitetura_mvc.puml`: arquitetura MVC usada pela implementação.

O código SQLAlchemy em `app/models.py` é a fonte de verdade da estrutura física; `docs/esquema_sqlite.sql` contém o DDL gerado a partir desse código.

As tabelas financeiras estão modeladas, mas a implementação dos serviços de crédito, distribuição, resgate, cupons e e-mails será finalizada na Sprint 03.
