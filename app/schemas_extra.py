"""Contratos de entrada da Sprint 03; validações no servidor."""
from pydantic import Field, field_validator
from app.schemas import ModelBase

class VantagemCriar(ModelBase):
    titulo: str = Field(min_length=3, max_length=150)
    descricao: str = Field(min_length=8, max_length=1500)
    foto_url: str = Field(min_length=8, max_length=500)
    custo: int = Field(ge=1, le=1000000)
    ativa: bool = True

    @field_validator('foto_url')
    @classmethod
    def url_segura(cls, value):
        if not value.startswith(('https://', 'http://')):
            raise ValueError('A foto precisa ter uma URL HTTP(S).')
        return value

class DistribuicaoCriar(ModelBase):
    aluno_id: str = Field(min_length=36, max_length=36)
    quantidade: int = Field(ge=1, le=1000000)
    motivo: str = Field(min_length=3, max_length=1000)

class ResgateCriar(ModelBase):
    vantagem_id: str = Field(min_length=36, max_length=36)

class UsoCupom(ModelBase):
    codigo: str = Field(min_length=6, max_length=64)
