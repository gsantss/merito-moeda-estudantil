"""Modelo relacional da Sprint 02 (prepara entidades futuras sem implementar os seus fluxos)."""
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import (
    String, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint,
    Text, Boolean, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def novo_id():
    return str(uuid4())


def agora():
    return datetime.now(timezone.utc)


class Instituicao(Base):
    __tablename__ = 'instituicoes'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    nome: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Usuario(Base):
    __tablename__ = 'usuarios'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    login: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(250), nullable=False)
    perfil: Mapped[str] = mapped_column(String(15), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, nullable=False)
    aluno: Mapped['Aluno | None'] = relationship(back_populates='usuario', uselist=False)
    professor: Mapped['Professor | None'] = relationship(back_populates='usuario', uselist=False)
    empresa: Mapped['EmpresaParceira | None'] = relationship(back_populates='usuario', uselist=False)
    carteira: Mapped['Carteira | None'] = relationship(back_populates='usuario', uselist=False)
    __table_args__ = (CheckConstraint("perfil IN ('aluno','professor','empresa')", name='ck_usuarios_perfil'),)


class Aluno(Base):
    __tablename__ = 'alunos'
    id: Mapped[str] = mapped_column(String(36), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)
    rg: Mapped[str] = mapped_column(String(30), nullable=False)
    endereco: Mapped[str] = mapped_column(String(240), nullable=False)
    curso: Mapped[str] = mapped_column(String(120), nullable=False)
    instituicao_id: Mapped[str] = mapped_column(ForeignKey('instituicoes.id', ondelete='RESTRICT'), nullable=False)
    usuario: Mapped[Usuario] = relationship(back_populates='aluno')
    instituicao: Mapped[Instituicao] = relationship()


class Professor(Base):
    __tablename__ = 'professores'
    id: Mapped[str] = mapped_column(String(36), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)
    departamento: Mapped[str] = mapped_column(String(130), nullable=False)
    instituicao_id: Mapped[str] = mapped_column(ForeignKey('instituicoes.id', ondelete='RESTRICT'), nullable=False)
    usuario: Mapped[Usuario] = relationship(back_populates='professor')
    instituicao: Mapped[Instituicao] = relationship()


class EmpresaParceira(Base):
    __tablename__ = 'empresas_parceiras'
    id: Mapped[str] = mapped_column(String(36), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    email_contato: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    cnpj: Mapped[str | None] = mapped_column(String(14), unique=True, nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    usuario: Mapped[Usuario] = relationship(back_populates='empresa')


class Carteira(Base):
    __tablename__ = 'carteiras'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    usuario_id: Mapped[str] = mapped_column(ForeignKey('usuarios.id', ondelete='RESTRICT'), unique=True, nullable=False)
    saldo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    atualizada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, nullable=False)
    usuario: Mapped[Usuario] = relationship(back_populates='carteira')
    __table_args__ = (CheckConstraint('saldo >= 0', name='ck_carteiras_saldo'),)


class TransacaoMoedas(Base):
    __tablename__ = 'transacoes_moedas'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    tipo: Mapped[str] = mapped_column(String(22), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    origem_carteira_id: Mapped[str | None] = mapped_column(ForeignKey('carteiras.id', ondelete='RESTRICT'))
    destino_carteira_id: Mapped[str | None] = mapped_column(ForeignKey('carteiras.id', ondelete='RESTRICT'))
    motivo: Mapped[str | None] = mapped_column(Text)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, nullable=False)
    semestre: Mapped[str | None] = mapped_column(String(7))
    __table_args__ = (
        CheckConstraint('quantidade > 0', name='ck_transacoes_quantidade'),
        CheckConstraint("tipo IN ('credito_semestral','distribuicao','resgate')", name='ck_transacoes_tipo'),
    )


class CreditoSemestral(Base):
    __tablename__ = 'creditos_semestrais'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    professor_id: Mapped[str] = mapped_column(ForeignKey('professores.id', ondelete='RESTRICT'), nullable=False)
    semestre: Mapped[str] = mapped_column(String(7), nullable=False)
    transacao_id: Mapped[str] = mapped_column(ForeignKey('transacoes_moedas.id', ondelete='RESTRICT'), unique=True, nullable=False)
    __table_args__ = (UniqueConstraint('professor_id', 'semestre', name='uq_credito_prof_semestre'),)


class Vantagem(Base):
    __tablename__ = 'vantagens'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    empresa_id: Mapped[str] = mapped_column(ForeignKey('empresas_parceiras.id', ondelete='RESTRICT'), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    foto_url: Mapped[str] = mapped_column(String(500), nullable=False)
    custo: Mapped[int] = mapped_column(Integer, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    __table_args__ = (CheckConstraint('custo > 0', name='ck_vantagens_custo'),)


class Resgate(Base):
    __tablename__ = 'resgates'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    aluno_id: Mapped[str] = mapped_column(ForeignKey('alunos.id', ondelete='RESTRICT'), nullable=False)
    vantagem_id: Mapped[str] = mapped_column(ForeignKey('vantagens.id', ondelete='RESTRICT'), nullable=False)
    transacao_id: Mapped[str] = mapped_column(ForeignKey('transacoes_moedas.id', ondelete='RESTRICT'), unique=True, nullable=False)
    custo_aplicado: Mapped[int] = mapped_column(Integer, nullable=False)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    __table_args__ = (CheckConstraint('custo_aplicado > 0', name='ck_resgates_custo'),)


class Cupom(Base):
    __tablename__ = 'cupons'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    resgate_id: Mapped[str] = mapped_column(ForeignKey('resgates.id', ondelete='RESTRICT'), unique=True, nullable=False)
    codigo: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    emitido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    utilizado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Notificacao(Base):
    __tablename__ = 'notificacoes'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    destinatario: Mapped[str] = mapped_column(String(150), nullable=False)
    assunto: Mapped[str] = mapped_column(String(200), nullable=False)
    corpo: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default='pendente')
    tentativas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    transacao_id: Mapped[str | None] = mapped_column(ForeignKey('transacoes_moedas.id', ondelete='RESTRICT'))
    cupom_id: Mapped[str | None] = mapped_column(ForeignKey('cupons.id', ondelete='RESTRICT'))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    __table_args__ = (CheckConstraint('tentativas >= 0', name='ck_notificacoes_tentativas'),)
