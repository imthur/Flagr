"""Testes unitários para as regras de avaliação de feature flags."""

from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest

from app.schemas.feature_flag import FeatureFlagResposta
from app.services.feature_flag_service import FeatureFlagService


def _criar_servico_mock() -> FeatureFlagService:
    """Cria um FeatureFlagService com DB e Redis mockados."""
    with patch("app.services.feature_flag_service.redis.Redis"):
        servico = FeatureFlagService(db=MagicMock())
    return servico


def _montar_flag(**kwargs) -> FeatureFlagResposta:
    defaults = {
        "id": 1,
        "name": "teste",
        "enabled": True,
        "rollout_percentage": None,
        "users": None,
        "created_at": datetime.now(),
        "updated_at": None,
    }
    return FeatureFlagResposta(**(defaults | kwargs))


class TestRegrasFlagDesativada:
    def test_flag_desativada_retorna_false(self):
        servico = _criar_servico_mock()
        flag = _montar_flag(enabled=False)
        servico.buscar_flag = MagicMock(return_value=flag)

        assert servico.avaliar_flag("teste", user_id=1) is False

    def test_flag_desativada_ignora_usuario_listado(self):
        servico = _criar_servico_mock()
        flag = _montar_flag(enabled=False, users=[1, 2, 3])
        servico.buscar_flag = MagicMock(return_value=flag)

        assert servico.avaliar_flag("teste", user_id=1) is False


class TestRegraUsuarioExplicito:
    def test_usuario_na_lista_retorna_true(self):
        servico = _criar_servico_mock()
        flag = _montar_flag(users=[10, 20, 30])
        servico.buscar_flag = MagicMock(return_value=flag)

        assert servico.avaliar_flag("teste", user_id=20) is True

    def test_usuario_fora_da_lista_nao_ativa_por_lista(self):
        servico = _criar_servico_mock()
        flag = _montar_flag(users=[10, 20])
        servico.buscar_flag = MagicMock(return_value=flag)

        # Sem rollout_percentage, cai no retorno global (enabled=True)
        assert servico.avaliar_flag("teste", user_id=99) is True


class TestRegraRolloutPercentual:
    def test_usuario_dentro_do_percentual(self):
        servico = _criar_servico_mock()
        flag = _montar_flag(rollout_percentage=100)
        servico.buscar_flag = MagicMock(return_value=flag)

        # 100% → todos os usuários ativados
        assert servico.avaliar_flag("teste", user_id=1) is True

    def test_usuario_fora_do_percentual(self):
        servico = _criar_servico_mock()
        flag = _montar_flag(rollout_percentage=0)
        servico.buscar_flag = MagicMock(return_value=flag)

        # 0% → nenhum usuário ativado
        assert servico.avaliar_flag("teste", user_id=1) is False

    def test_rollout_determinístico(self):
        """Mesmo usuário deve receber mesmo resultado em chamadas repetidas."""
        servico = _criar_servico_mock()
        flag = _montar_flag(rollout_percentage=50)
        servico.buscar_flag = MagicMock(return_value=flag)

        resultado1 = servico.avaliar_flag("teste", user_id=42)
        resultado2 = servico.avaliar_flag("teste", user_id=42)
        assert resultado1 == resultado2


class TestRegraFallbackGlobal:
    def test_sem_rollout_sem_usuarios_retorna_enabled(self):
        servico = _criar_servico_mock()
        flag = _montar_flag(enabled=True, rollout_percentage=None, users=None)
        servico.buscar_flag = MagicMock(return_value=flag)

        assert servico.avaliar_flag("teste", user_id=999) is True
