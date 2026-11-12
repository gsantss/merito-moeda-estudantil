-- Modelo físico atualizado da Sprint 03 (12 tabelas); gerado via SQLAlchemy


CREATE TABLE instituicoes (
	id VARCHAR(36) NOT NULL, 
	nome VARCHAR(150) NOT NULL, 
	ativa BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
)

;


CREATE TABLE usuarios (
	id VARCHAR(36) NOT NULL, 
	login VARCHAR(120) NOT NULL, 
	senha_hash VARCHAR(250) NOT NULL, 
	perfil VARCHAR(15) NOT NULL, 
	ativo BOOLEAN NOT NULL, 
	criado_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_usuarios_perfil CHECK (perfil IN ('aluno','professor','empresa'))
)

;

CREATE UNIQUE INDEX ix_usuarios_login ON usuarios (login);


CREATE TABLE alunos (
	id VARCHAR(36) NOT NULL, 
	nome VARCHAR(150) NOT NULL, 
	email VARCHAR(150) NOT NULL, 
	cpf VARCHAR(11) NOT NULL, 
	rg VARCHAR(30) NOT NULL, 
	endereco VARCHAR(240) NOT NULL, 
	curso VARCHAR(120) NOT NULL, 
	instituicao_id VARCHAR(36) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(id) REFERENCES usuarios (id) ON DELETE CASCADE, 
	UNIQUE (cpf), 
	FOREIGN KEY(instituicao_id) REFERENCES instituicoes (id) ON DELETE RESTRICT
)

;

CREATE UNIQUE INDEX ix_alunos_email ON alunos (email);


CREATE TABLE carteiras (
	id VARCHAR(36) NOT NULL, 
	usuario_id VARCHAR(36) NOT NULL, 
	saldo INTEGER NOT NULL, 
	atualizada_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_carteiras_saldo CHECK (saldo >= 0), 
	UNIQUE (usuario_id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id) ON DELETE RESTRICT
)

;


CREATE TABLE empresas_parceiras (
	id VARCHAR(36) NOT NULL, 
	nome VARCHAR(160) NOT NULL, 
	email_contato VARCHAR(150) NOT NULL, 
	cnpj VARCHAR(14), 
	descricao TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(id) REFERENCES usuarios (id) ON DELETE CASCADE, 
	UNIQUE (email_contato), 
	UNIQUE (cnpj)
)

;


CREATE TABLE professores (
	id VARCHAR(36) NOT NULL, 
	nome VARCHAR(150) NOT NULL, 
	cpf VARCHAR(11) NOT NULL, 
	departamento VARCHAR(130) NOT NULL, 
	instituicao_id VARCHAR(36) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(id) REFERENCES usuarios (id) ON DELETE CASCADE, 
	UNIQUE (cpf), 
	FOREIGN KEY(instituicao_id) REFERENCES instituicoes (id) ON DELETE RESTRICT
)

;


CREATE TABLE transacoes_moedas (
	id VARCHAR(36) NOT NULL, 
	tipo VARCHAR(22) NOT NULL, 
	quantidade INTEGER NOT NULL, 
	origem_carteira_id VARCHAR(36), 
	destino_carteira_id VARCHAR(36), 
	motivo TEXT, 
	data_hora DATETIME NOT NULL, 
	semestre VARCHAR(7), 
	PRIMARY KEY (id), 
	CONSTRAINT ck_transacoes_quantidade CHECK (quantidade > 0), 
	CONSTRAINT ck_transacoes_tipo CHECK (tipo IN ('credito_semestral','distribuicao','resgate')), 
	FOREIGN KEY(origem_carteira_id) REFERENCES carteiras (id) ON DELETE RESTRICT, 
	FOREIGN KEY(destino_carteira_id) REFERENCES carteiras (id) ON DELETE RESTRICT
)

;


CREATE TABLE vantagens (
	id VARCHAR(36) NOT NULL, 
	empresa_id VARCHAR(36) NOT NULL, 
	titulo VARCHAR(150) NOT NULL, 
	descricao TEXT NOT NULL, 
	foto_url VARCHAR(500) NOT NULL, 
	custo INTEGER NOT NULL, 
	ativa BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_vantagens_custo CHECK (custo > 0), 
	FOREIGN KEY(empresa_id) REFERENCES empresas_parceiras (id) ON DELETE RESTRICT
)

;


CREATE TABLE creditos_semestrais (
	id VARCHAR(36) NOT NULL, 
	professor_id VARCHAR(36) NOT NULL, 
	semestre VARCHAR(7) NOT NULL, 
	transacao_id VARCHAR(36) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_credito_prof_semestre UNIQUE (professor_id, semestre), 
	FOREIGN KEY(professor_id) REFERENCES professores (id) ON DELETE RESTRICT, 
	UNIQUE (transacao_id), 
	FOREIGN KEY(transacao_id) REFERENCES transacoes_moedas (id) ON DELETE RESTRICT
)

;


CREATE TABLE resgates (
	id VARCHAR(36) NOT NULL, 
	aluno_id VARCHAR(36) NOT NULL, 
	vantagem_id VARCHAR(36) NOT NULL, 
	transacao_id VARCHAR(36) NOT NULL, 
	custo_aplicado INTEGER NOT NULL, 
	data_hora DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_resgates_custo CHECK (custo_aplicado > 0), 
	FOREIGN KEY(aluno_id) REFERENCES alunos (id) ON DELETE RESTRICT, 
	FOREIGN KEY(vantagem_id) REFERENCES vantagens (id) ON DELETE RESTRICT, 
	UNIQUE (transacao_id), 
	FOREIGN KEY(transacao_id) REFERENCES transacoes_moedas (id) ON DELETE RESTRICT
)

;


CREATE TABLE cupons (
	id VARCHAR(36) NOT NULL, 
	resgate_id VARCHAR(36) NOT NULL, 
	codigo VARCHAR(64) NOT NULL, 
	emitido_em DATETIME NOT NULL, 
	utilizado_em DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (resgate_id), 
	FOREIGN KEY(resgate_id) REFERENCES resgates (id) ON DELETE RESTRICT, 
	UNIQUE (codigo)
)

;


CREATE TABLE notificacoes (
	id VARCHAR(36) NOT NULL, 
	destinatario VARCHAR(150) NOT NULL, 
	assunto VARCHAR(200) NOT NULL, 
	corpo TEXT NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	tentativas INTEGER NOT NULL, 
	transacao_id VARCHAR(36), 
	cupom_id VARCHAR(36), 
	criado_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_notificacoes_tentativas CHECK (tentativas >= 0), 
	FOREIGN KEY(transacao_id) REFERENCES transacoes_moedas (id) ON DELETE RESTRICT, 
	FOREIGN KEY(cupom_id) REFERENCES cupons (id) ON DELETE RESTRICT
)

;

