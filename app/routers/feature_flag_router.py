from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import obter_db
from app.schemas.feature_flag import (
    AvaliacaoResposta,
    FeatureFlagAtualizar,
    FeatureFlagCriar,
    FeatureFlagResposta,
)
from app.services.feature_flag_service import FeatureFlagService

router = APIRouter(prefix="/flags", tags=["Feature Flags"])


def _obter_servico(db: Session = Depends(obter_db)) -> FeatureFlagService:
    return FeatureFlagService(db)


@router.post("/", response_model=FeatureFlagResposta, status_code=201, summary="Criar flag")
def criar_flag(
    dados: FeatureFlagCriar,
    servico: FeatureFlagService = Depends(_obter_servico),
) -> FeatureFlagResposta:
    """Cria uma nova feature flag."""
    return servico.criar_flag(dados)


@router.get("/", response_model=List[FeatureFlagResposta], summary="Listar flags")
def listar_flags(
    servico: FeatureFlagService = Depends(_obter_servico),
) -> List[FeatureFlagResposta]:
    """Retorna todas as feature flags cadastradas."""
    return servico.listar_flags()


@router.get("/{nome}", response_model=FeatureFlagResposta, summary="Buscar flag")
def buscar_flag(
    nome: str,
    servico: FeatureFlagService = Depends(_obter_servico),
) -> FeatureFlagResposta:
    """Busca uma feature flag pelo nome."""
    return servico.buscar_flag(nome)


@router.get("/{nome}/evaluate", response_model=AvaliacaoResposta, summary="Avaliar flag")
def avaliar_flag(
    nome: str,
    user_id: int = Query(..., description="ID do usuário a ser avaliado"),
    servico: FeatureFlagService = Depends(_obter_servico),
) -> AvaliacaoResposta:
    """Avalia se a feature flag está ativa para o usuário informado."""
    resultado = servico.avaliar_flag(nome, user_id)
    return AvaliacaoResposta(enabled=resultado)


@router.put("/{flag_id}", response_model=FeatureFlagResposta, summary="Atualizar flag")
def atualizar_flag(
    flag_id: int,
    dados: FeatureFlagAtualizar,
    servico: FeatureFlagService = Depends(_obter_servico),
) -> FeatureFlagResposta:
    """Atualiza os campos de uma feature flag pelo ID."""
    return servico.atualizar_flag(flag_id, dados)
