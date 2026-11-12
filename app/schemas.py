from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

# EmailStr precisa de email-validator, por isso os emails são validados sem dependências extras.
class ModelBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


def validar_email(v):
    v = v.strip().lower()
    if len(v) > 150 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', v):
        raise ValueError('Informe um endereço de e-mail válido.')
    return v


def validar_cpf(v):
    numeros = re.sub(r'\D', '', v)
    if len(numeros) != 11 or len(set(numeros)) == 1:
        raise ValueError('Informe um CPF válido com 11 dígitos.')
    for tamanho in (9, 10):
        pesos = range(tamanho + 1, 1, -1)
        resto = (sum(int(n) * p for n, p in zip(numeros[:tamanho], pesos)) * 10) % 11
        if resto == 10: resto = 0
        if resto != int(numeros[tamanho]):
            raise ValueError('Os dígitos verificadores do CPF são inválidos.')
    return numeros


def validar_cnpj(v):
    if v is None or not v.strip():
        return None
    numeros = re.sub(r'\D', '', v)
    if len(numeros) != 14 or len(set(numeros)) == 1:
        raise ValueError('Informe um CNPJ válido com 14 dígitos.')
    for tamanho, pesos in ((12, [5,4,3,2,9,8,7,6,5,4,3,2]), (13, [6,5,4,3,2,9,8,7,6,5,4,3,2])):
        resto = sum(int(n) * p for n, p in zip(numeros[:tamanho], pesos)) % 11
        digito = 0 if resto < 2 else 11 - resto
        if digito != int(numeros[tamanho]):
            raise ValueError('Os dígitos verificadores do CNPJ são inválidos.')
    return numeros


class AlunoCriar(ModelBase):
    nome: str = Field(min_length=3, max_length=150)
    email: str = Field(min_length=6, max_length=150)
    cpf: str = Field(min_length=11, max_length=18)
    rg: str = Field(min_length=3, max_length=30)
    endereco: str = Field(min_length=5, max_length=240)
    curso: str = Field(min_length=2, max_length=120)
    instituicao_id: str
    login: str = Field(min_length=3, max_length=120)
    senha: str = Field(min_length=8, max_length=128)

    _email = field_validator('email')(validar_email)
    _cpf = field_validator('cpf')(validar_cpf)


class AlunoAtualizar(ModelBase):
    nome: str = Field(min_length=3, max_length=150)
    email: str = Field(min_length=6, max_length=150)
    rg: str = Field(min_length=3, max_length=30)
    endereco: str = Field(min_length=5, max_length=240)
    curso: str = Field(min_length=2, max_length=120)
    instituicao_id: str
    senha_nova: str | None = Field(default=None, min_length=8, max_length=128)
    _email = field_validator('email')(validar_email)


class EmpresaCriar(ModelBase):
    nome: str = Field(min_length=2, max_length=160)
    email_contato: str = Field(min_length=6, max_length=150)
    cnpj: str | None = None
    descricao: str | None = Field(default=None, max_length=1000)
    login: str = Field(min_length=3, max_length=120)
    senha: str = Field(min_length=8, max_length=128)
    _email = field_validator('email_contato')(validar_email)
    _cnpj = field_validator('cnpj')(validar_cnpj)


class EmpresaAtualizar(ModelBase):
    nome: str = Field(min_length=2, max_length=160)
    email_contato: str = Field(min_length=6, max_length=150)
    cnpj: str | None = None
    descricao: str | None = Field(default=None, max_length=1000)
    senha_nova: str | None = Field(default=None, min_length=8, max_length=128)
    _email = field_validator('email_contato')(validar_email)
    _cnpj = field_validator('cnpj')(validar_cnpj)


class LoginPayload(ModelBase):
    login: str = Field(min_length=1, max_length=120)
    senha: str = Field(min_length=1)
