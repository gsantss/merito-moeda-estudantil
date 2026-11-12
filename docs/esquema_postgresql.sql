-- Estrutura do banco PostgreSQL usada na nuvem (Render), gerada pelo SQLAlchemy (app/models.py)
-- na primeira inicialização da API. Arquivo apenas para consulta; complementa esquema_sqlite.sql.
-- Gerado com: pg_dump --schema-only --no-owner --no-privileges

-- Name: alunos; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.alunos (
    id character varying(36) NOT NULL,
    nome character varying(150) NOT NULL,
    email character varying(150) NOT NULL,
    cpf character varying(11) NOT NULL,
    rg character varying(30) NOT NULL,
    endereco character varying(240) NOT NULL,
    curso character varying(120) NOT NULL,
    instituicao_id character varying(36) NOT NULL
);

-- Name: carteiras; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.carteiras (
    id character varying(36) NOT NULL,
    usuario_id character varying(36) NOT NULL,
    saldo integer NOT NULL,
    atualizada_em timestamp with time zone NOT NULL,
    CONSTRAINT ck_carteiras_saldo CHECK ((saldo >= 0))
);

-- Name: creditos_semestrais; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.creditos_semestrais (
    id character varying(36) NOT NULL,
    professor_id character varying(36) NOT NULL,
    semestre character varying(7) NOT NULL,
    transacao_id character varying(36) NOT NULL
);

-- Name: cupons; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.cupons (
    id character varying(36) NOT NULL,
    resgate_id character varying(36) NOT NULL,
    codigo character varying(64) NOT NULL,
    emitido_em timestamp with time zone NOT NULL,
    utilizado_em timestamp with time zone
);

-- Name: empresas_parceiras; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.empresas_parceiras (
    id character varying(36) NOT NULL,
    nome character varying(160) NOT NULL,
    email_contato character varying(150) NOT NULL,
    cnpj character varying(14),
    descricao text
);

-- Name: instituicoes; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.instituicoes (
    id character varying(36) NOT NULL,
    nome character varying(150) NOT NULL,
    ativa boolean NOT NULL
);

-- Name: notificacoes; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.notificacoes (
    id character varying(36) NOT NULL,
    destinatario character varying(150) NOT NULL,
    assunto character varying(200) NOT NULL,
    corpo text NOT NULL,
    status character varying(16) NOT NULL,
    tentativas integer NOT NULL,
    transacao_id character varying(36),
    cupom_id character varying(36),
    criado_em timestamp with time zone NOT NULL,
    CONSTRAINT ck_notificacoes_tentativas CHECK ((tentativas >= 0))
);

-- Name: professores; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.professores (
    id character varying(36) NOT NULL,
    nome character varying(150) NOT NULL,
    cpf character varying(11) NOT NULL,
    departamento character varying(130) NOT NULL,
    instituicao_id character varying(36) NOT NULL
);

-- Name: resgates; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.resgates (
    id character varying(36) NOT NULL,
    aluno_id character varying(36) NOT NULL,
    vantagem_id character varying(36) NOT NULL,
    transacao_id character varying(36) NOT NULL,
    custo_aplicado integer NOT NULL,
    data_hora timestamp with time zone NOT NULL,
    CONSTRAINT ck_resgates_custo CHECK ((custo_aplicado > 0))
);

-- Name: transacoes_moedas; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.transacoes_moedas (
    id character varying(36) NOT NULL,
    tipo character varying(22) NOT NULL,
    quantidade integer NOT NULL,
    origem_carteira_id character varying(36),
    destino_carteira_id character varying(36),
    motivo text,
    data_hora timestamp with time zone NOT NULL,
    semestre character varying(7),
    CONSTRAINT ck_transacoes_quantidade CHECK ((quantidade > 0)),
    CONSTRAINT ck_transacoes_tipo CHECK (((tipo)::text = ANY ((ARRAY['credito_semestral'::character varying, 'distribuicao'::character varying, 'resgate'::character varying])::text[])))
);

-- Name: usuarios; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.usuarios (
    id character varying(36) NOT NULL,
    login character varying(120) NOT NULL,
    senha_hash character varying(250) NOT NULL,
    perfil character varying(15) NOT NULL,
    ativo boolean NOT NULL,
    criado_em timestamp with time zone NOT NULL,
    CONSTRAINT ck_usuarios_perfil CHECK (((perfil)::text = ANY ((ARRAY['aluno'::character varying, 'professor'::character varying, 'empresa'::character varying])::text[])))
);

-- Name: vantagens; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.vantagens (
    id character varying(36) NOT NULL,
    empresa_id character varying(36) NOT NULL,
    titulo character varying(150) NOT NULL,
    descricao text NOT NULL,
    foto_url character varying(500) NOT NULL,
    custo integer NOT NULL,
    ativa boolean NOT NULL,
    CONSTRAINT ck_vantagens_custo CHECK ((custo > 0))
);

-- Name: alunos alunos_cpf_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.alunos
    ADD CONSTRAINT alunos_cpf_key UNIQUE (cpf);

-- Name: alunos alunos_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.alunos
    ADD CONSTRAINT alunos_pkey PRIMARY KEY (id);

-- Name: carteiras carteiras_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.carteiras
    ADD CONSTRAINT carteiras_pkey PRIMARY KEY (id);

-- Name: carteiras carteiras_usuario_id_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.carteiras
    ADD CONSTRAINT carteiras_usuario_id_key UNIQUE (usuario_id);

-- Name: creditos_semestrais creditos_semestrais_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.creditos_semestrais
    ADD CONSTRAINT creditos_semestrais_pkey PRIMARY KEY (id);

-- Name: creditos_semestrais creditos_semestrais_transacao_id_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.creditos_semestrais
    ADD CONSTRAINT creditos_semestrais_transacao_id_key UNIQUE (transacao_id);

-- Name: cupons cupons_codigo_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.cupons
    ADD CONSTRAINT cupons_codigo_key UNIQUE (codigo);

-- Name: cupons cupons_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.cupons
    ADD CONSTRAINT cupons_pkey PRIMARY KEY (id);

-- Name: cupons cupons_resgate_id_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.cupons
    ADD CONSTRAINT cupons_resgate_id_key UNIQUE (resgate_id);

-- Name: empresas_parceiras empresas_parceiras_cnpj_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.empresas_parceiras
    ADD CONSTRAINT empresas_parceiras_cnpj_key UNIQUE (cnpj);

-- Name: empresas_parceiras empresas_parceiras_email_contato_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.empresas_parceiras
    ADD CONSTRAINT empresas_parceiras_email_contato_key UNIQUE (email_contato);

-- Name: empresas_parceiras empresas_parceiras_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.empresas_parceiras
    ADD CONSTRAINT empresas_parceiras_pkey PRIMARY KEY (id);

-- Name: instituicoes instituicoes_nome_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.instituicoes
    ADD CONSTRAINT instituicoes_nome_key UNIQUE (nome);

-- Name: instituicoes instituicoes_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.instituicoes
    ADD CONSTRAINT instituicoes_pkey PRIMARY KEY (id);

-- Name: notificacoes notificacoes_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.notificacoes
    ADD CONSTRAINT notificacoes_pkey PRIMARY KEY (id);

-- Name: professores professores_cpf_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.professores
    ADD CONSTRAINT professores_cpf_key UNIQUE (cpf);

-- Name: professores professores_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.professores
    ADD CONSTRAINT professores_pkey PRIMARY KEY (id);

-- Name: resgates resgates_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.resgates
    ADD CONSTRAINT resgates_pkey PRIMARY KEY (id);

-- Name: resgates resgates_transacao_id_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.resgates
    ADD CONSTRAINT resgates_transacao_id_key UNIQUE (transacao_id);

-- Name: transacoes_moedas transacoes_moedas_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.transacoes_moedas
    ADD CONSTRAINT transacoes_moedas_pkey PRIMARY KEY (id);

-- Name: creditos_semestrais uq_credito_prof_semestre; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.creditos_semestrais
    ADD CONSTRAINT uq_credito_prof_semestre UNIQUE (professor_id, semestre);

-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);

-- Name: vantagens vantagens_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.vantagens
    ADD CONSTRAINT vantagens_pkey PRIMARY KEY (id);

-- Name: ix_alunos_email; Type: INDEX; Schema: public; Owner: -

CREATE UNIQUE INDEX ix_alunos_email ON public.alunos USING btree (email);

-- Name: ix_usuarios_login; Type: INDEX; Schema: public; Owner: -

CREATE UNIQUE INDEX ix_usuarios_login ON public.usuarios USING btree (login);

-- Name: alunos alunos_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.alunos
    ADD CONSTRAINT alunos_id_fkey FOREIGN KEY (id) REFERENCES public.usuarios(id) ON DELETE CASCADE;

-- Name: alunos alunos_instituicao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.alunos
    ADD CONSTRAINT alunos_instituicao_id_fkey FOREIGN KEY (instituicao_id) REFERENCES public.instituicoes(id) ON DELETE RESTRICT;

-- Name: carteiras carteiras_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.carteiras
    ADD CONSTRAINT carteiras_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;

-- Name: creditos_semestrais creditos_semestrais_professor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.creditos_semestrais
    ADD CONSTRAINT creditos_semestrais_professor_id_fkey FOREIGN KEY (professor_id) REFERENCES public.professores(id) ON DELETE RESTRICT;

-- Name: creditos_semestrais creditos_semestrais_transacao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.creditos_semestrais
    ADD CONSTRAINT creditos_semestrais_transacao_id_fkey FOREIGN KEY (transacao_id) REFERENCES public.transacoes_moedas(id) ON DELETE RESTRICT;

-- Name: cupons cupons_resgate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.cupons
    ADD CONSTRAINT cupons_resgate_id_fkey FOREIGN KEY (resgate_id) REFERENCES public.resgates(id) ON DELETE RESTRICT;

-- Name: empresas_parceiras empresas_parceiras_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.empresas_parceiras
    ADD CONSTRAINT empresas_parceiras_id_fkey FOREIGN KEY (id) REFERENCES public.usuarios(id) ON DELETE CASCADE;

-- Name: notificacoes notificacoes_cupom_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.notificacoes
    ADD CONSTRAINT notificacoes_cupom_id_fkey FOREIGN KEY (cupom_id) REFERENCES public.cupons(id) ON DELETE RESTRICT;

-- Name: notificacoes notificacoes_transacao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.notificacoes
    ADD CONSTRAINT notificacoes_transacao_id_fkey FOREIGN KEY (transacao_id) REFERENCES public.transacoes_moedas(id) ON DELETE RESTRICT;

-- Name: professores professores_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.professores
    ADD CONSTRAINT professores_id_fkey FOREIGN KEY (id) REFERENCES public.usuarios(id) ON DELETE CASCADE;

-- Name: professores professores_instituicao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.professores
    ADD CONSTRAINT professores_instituicao_id_fkey FOREIGN KEY (instituicao_id) REFERENCES public.instituicoes(id) ON DELETE RESTRICT;

-- Name: resgates resgates_aluno_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.resgates
    ADD CONSTRAINT resgates_aluno_id_fkey FOREIGN KEY (aluno_id) REFERENCES public.alunos(id) ON DELETE RESTRICT;

-- Name: resgates resgates_transacao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.resgates
    ADD CONSTRAINT resgates_transacao_id_fkey FOREIGN KEY (transacao_id) REFERENCES public.transacoes_moedas(id) ON DELETE RESTRICT;

-- Name: resgates resgates_vantagem_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.resgates
    ADD CONSTRAINT resgates_vantagem_id_fkey FOREIGN KEY (vantagem_id) REFERENCES public.vantagens(id) ON DELETE RESTRICT;

-- Name: transacoes_moedas transacoes_moedas_destino_carteira_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.transacoes_moedas
    ADD CONSTRAINT transacoes_moedas_destino_carteira_id_fkey FOREIGN KEY (destino_carteira_id) REFERENCES public.carteiras(id) ON DELETE RESTRICT;

-- Name: transacoes_moedas transacoes_moedas_origem_carteira_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.transacoes_moedas
    ADD CONSTRAINT transacoes_moedas_origem_carteira_id_fkey FOREIGN KEY (origem_carteira_id) REFERENCES public.carteiras(id) ON DELETE RESTRICT;

-- Name: vantagens vantagens_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.vantagens
    ADD CONSTRAINT vantagens_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas_parceiras(id) ON DELETE RESTRICT;

