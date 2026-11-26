"""Serviço de domínio para cadastro, listagem e manutenção de vantagens."""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import EmpresaParceira, Vantagem
from app.repositories import vantagens as repo
from app.schemas_extra import VantagemCriar


def apresentar(v: Vantagem, empresa_nome: str = '') -> dict:
    """Serializa uma vantagem para o contrato público/privado da API."""
    return {
        'id': v.id,
        'empresa_id': v.empresa_id,
        'empresa': empresa_nome,
        'titulo': v.titulo,
        'descricao': v.descricao,
        'foto_url': v.foto_url,
        'custo': v.custo,
        'ativa': v.ativa,
    }


def _obter_propria(db: Session, empresa_id: str, vantagem_id: str, mensagem_proibido: str) -> Vantagem:
    v = repo.por_id(db, vantagem_id)
    if not v:
        raise HTTPException(404, 'Vantagem não encontrada.')
    if v.empresa_id != empresa_id:
        raise HTTPException(403, mensagem_proibido)
    return v


def listar_ativas(db: Session) -> list[dict]:
    return [apresentar(v, e.nome) for v, e in repo.listar_ativas_com_empresa(db)]


def listar_da_empresa(db: Session, empresa_id: str) -> list[dict]:
    return [apresentar(v) for v in repo.por_empresa(db, empresa_id)]


def criar(db: Session, empresa: EmpresaParceira, payload: VantagemCriar) -> dict:
    v = Vantagem(empresa_id=empresa.id, **payload.model_dump())
    db.add(v)
    db.commit()
    db.refresh(v)
    return apresentar(v, empresa.nome)


def atualizar(db: Session, empresa: EmpresaParceira, vantagem_id: str, payload: VantagemCriar) -> dict:
    v = _obter_propria(db, empresa.id, vantagem_id, 'Você só pode editar vantagens próprias.')
    for campo, valor in payload.model_dump().items():
        setattr(v, campo, valor)
    db.commit()
    db.refresh(v)
    return apresentar(v, empresa.nome)


def desativar(db: Session, empresa_id: str, vantagem_id: str) -> dict:
    # Arquivamento preserva relação com resgates anteriores.
    v = _obter_propria(db, empresa_id, vantagem_id, 'Você só pode excluir vantagens próprias.')
    v.ativa = False
    db.commit()
    return {'mensagem': 'Vantagem desativada. Registros de resgates preservados.'}
