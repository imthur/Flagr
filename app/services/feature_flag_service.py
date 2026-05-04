import json
import logging
from typing import List, Optional

import redis
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import configuracoes
from app.repositories.feature_flag_repository import FeatureFlagRepository
from app.schemas.feature_flag import (
    AvaliacaoResposta,
    FeatureFlagAtualizar,
    FeatureFlagCriar,
    FeatureFlagResposta,
)
from app.utils.hashing import calcular_hash_rollout

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """Camada de serviço: contém toda a lógica de negócio e gerencia o cache Redis."""

    PREFIXO_CACHE = "feature_flag:"
    TTL_CACHE = 300  # 5 minutos

    def __init__(self, db: Session) -> None:
        self.repositorio = FeatureFlagRepository(db)
        self.cache = redis.from_url(configuracoes.redis_url, decode_responses=True)

    # --- Cache ---

    def _chave_cache(self, nome: str) -> str:
        return f"{self.PREFIXO_CACHE}{nome}"

    def _obter_do_cache(self, nome: str) -> Optional[FeatureFlagResposta]:
        try:
            dados = self.cache.get(self._chave_cache(nome))
            if dados:
                return FeatureFlagResposta(**json.loads(dados))
        except redis.RedisError as e:
            logger.warning("Falha ao ler cache Redis: %s", e)
        return None

    def _salvar_no_cache(self, flag: FeatureFlagResposta) -> None:
        try:
            self.cache.setex(
                self._chave_cache(flag.name),
                self.TTL_CACHE,
                flag.model_dump_json(),
            )
        except redis.RedisError as e:
            logger.warning("Falha ao gravar cache Redis: %s", e)

    def _invalidar_cache(self, nome: str) -> None:
        try:
            self.cache.delete(self._chave_cache(nome))
        except redis.RedisError as e:
            logger.warning("Falha ao invalidar cache Redis: %s", e)

    # --- CRUD ---

    def criar_flag(self, dados: FeatureFlagCriar) -> FeatureFlagResposta:
        """Cria uma nova feature flag."""
        flag = self.repositorio.criar(dados)
        return FeatureFlagResposta.model_validate(flag)

    def listar_flags(self) -> List[FeatureFlagResposta]:
        """Retorna todas as feature flags."""
        return [FeatureFlagResposta.model_validate(f) for f in self.repositorio.listar()]

    def buscar_flag(self, nome: str) -> FeatureFlagResposta:
        """Busca uma flag pelo nome, com fallback para banco se não estiver em cache."""
        flag_cache = self._obter_do_cache(nome)
        if flag_cache:
            return flag_cache

        flag = self.repositorio.buscar_por_nome(nome)
        if not flag:
            raise HTTPException(status_code=404, detail=f"Flag '{nome}' não encontrada")

        resposta = FeatureFlagResposta.model_validate(flag)
        self._salvar_no_cache(resposta)
        return resposta

    def atualizar_flag(self, flag_id: int, dados: FeatureFlagAtualizar) -> FeatureFlagResposta:
        """Atualiza uma flag e invalida o cache correspondente."""
        flag_existente = self.repositorio.buscar_por_id(flag_id)
        if not flag_existente:
            raise HTTPException(status_code=404, detail=f"Flag ID {flag_id} não encontrada")

        flag_atualizada = self.repositorio.atualizar(flag_id, dados)
        self._invalidar_cache(flag_existente.name)
        return FeatureFlagResposta.model_validate(flag_atualizada)

    # --- Avaliação ---

    def avaliar_flag(self, nome: str, user_id: int) -> bool:
        """Avalia se a flag está ativa para o usuário seguindo a ordem de prioridade:

        1. Flag desativada → False
        2. Usuário listado explicitamente → True
        3. Rollout percentual determinístico → hash(user_id + flag_name) % 100 < percentual
        4. Fallback para estado global (enabled)
        """
        flag = self.buscar_flag(nome)

        if not flag.enabled:
            return False

        if flag.users and user_id in flag.users:
            return True

        if flag.rollout_percentage is not None:
            percentil = calcular_hash_rollout(user_id, nome)
            return percentil < flag.rollout_percentage

        return flag.enabled
