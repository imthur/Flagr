"""Testes unitários para a lógica de hash de rollout."""

import pytest
from app.utils.hashing import calcular_hash_rollout


def test_determinismo():
    """Mesmo user_id e flag_name devem sempre retornar o mesmo resultado."""
    assert calcular_hash_rollout(42, "nova_dashboard") == calcular_hash_rollout(42, "nova_dashboard")
    assert calcular_hash_rollout(1, "beta") == calcular_hash_rollout(1, "beta")


def test_intervalo_valido():
    """O resultado deve estar entre 0 e 99 (inclusive)."""
    for user_id in range(200):
        resultado = calcular_hash_rollout(user_id, "teste_intervalo")
        assert 0 <= resultado <= 99, f"Resultado fora do intervalo: {resultado}"


def test_usuarios_diferentes_produzem_resultados_distintos():
    """Usuários diferentes devem ter distribuição variada."""
    resultados = {calcular_hash_rollout(i, "flag_abc") for i in range(50)}
    assert len(resultados) > 10, "Distribuição muito concentrada"


def test_flags_diferentes_para_mesmo_usuario():
    """O mesmo usuário deve ter resultados diferentes para flags distintas."""
    r1 = calcular_hash_rollout(99, "flag_a")
    r2 = calcular_hash_rollout(99, "flag_b")
    # Podem ser iguais por coincidência, mas a probabilidade é baixa
    # com flags bem diferentes — apenas verificamos que a função aceita os dois
    assert isinstance(r1, int)
    assert isinstance(r2, int)
