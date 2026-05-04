from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FeatureFlagCriar(BaseModel):
    """Schema para criação de uma nova feature flag."""

    name: str = Field(..., min_length=1, max_length=100, description="Identificador único da flag")
    enabled: bool = Field(default=False, description="Estado global da flag")
    rollout_percentage: Optional[int] = Field(
        default=None, ge=0, le=100, description="Percentual de ativação (0-100)"
    )
    users: Optional[List[int]] = Field(
        default=None, description="Lista de IDs de usuários com acesso explícito"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Rollout para 30% dos usuários",
                    "value": {"name": "novo-checkout", "enabled": True, "rollout_percentage": 30},
                },
                {
                    "summary": "Ativação para usuários específicos",
                    "value": {"name": "beta-dashboard", "enabled": True, "users": [1, 2, 99]},
                },
                {
                    "summary": "Flag global ligada",
                    "value": {"name": "dark-mode", "enabled": True},
                },
            ]
        }
    }


class FeatureFlagAtualizar(BaseModel):
    """Schema para atualização parcial de uma feature flag."""

    enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    users: Optional[List[int]] = None


class FeatureFlagResposta(BaseModel):
    """Schema de resposta de uma feature flag."""

    id: int
    name: str
    enabled: bool
    rollout_percentage: Optional[int]
    users: Optional[List[int]]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AvaliacaoResposta(BaseModel):
    """Resultado da avaliação de uma flag para um usuário."""

    enabled: bool
