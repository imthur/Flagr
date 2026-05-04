"""Testes de integração para os endpoints da Feature Flags API."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, obter_db

DATABASE_URL_TESTE = "sqlite:///./test_flags.db"

engine_teste = create_engine(DATABASE_URL_TESTE, connect_args={"check_same_thread": False})
SessaoTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)


def substituir_db():
    db = SessaoTeste()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_banco():
    Base.metadata.create_all(bind=engine_teste)
    yield
    Base.metadata.drop_all(bind=engine_teste)


@pytest.fixture()
def cliente():
    app.dependency_overrides[obter_db] = substituir_db
    with patch("app.services.feature_flag_service.redis.Redis") as mock_redis:
        mock_redis.return_value = MagicMock(get=MagicMock(return_value=None), setex=MagicMock(), delete=MagicMock())
        with TestClient(app) as c:
            yield c
    app.dependency_overrides.clear()


# --- Testes de criação ---

def test_criar_flag(cliente):
    resposta = cliente.post("/flags/", json={"name": "nova_ui", "enabled": True})
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["name"] == "nova_ui"
    assert dados["enabled"] is True


def test_criar_flag_duplicada_retorna_erro(cliente):
    cliente.post("/flags/", json={"name": "duplicada", "enabled": False})
    resposta = cliente.post("/flags/", json={"name": "duplicada", "enabled": True})
    assert resposta.status_code in (400, 409, 422, 500)


def test_criar_flag_com_rollout_invalido(cliente):
    resposta = cliente.post("/flags/", json={"name": "invalida", "enabled": True, "rollout_percentage": 150})
    assert resposta.status_code == 422


# --- Testes de listagem ---

def test_listar_flags_vazio(cliente):
    resposta = cliente.get("/flags/")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_listar_flags_com_dados(cliente):
    cliente.post("/flags/", json={"name": "flag_a", "enabled": True})
    cliente.post("/flags/", json={"name": "flag_b", "enabled": False})
    resposta = cliente.get("/flags/")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


# --- Testes de busca ---

def test_buscar_flag_existente(cliente):
    cliente.post("/flags/", json={"name": "busca_teste", "enabled": True})
    resposta = cliente.get("/flags/busca_teste")
    assert resposta.status_code == 200
    assert resposta.json()["name"] == "busca_teste"


def test_buscar_flag_inexistente(cliente):
    resposta = cliente.get("/flags/nao_existe")
    assert resposta.status_code == 404


# --- Testes de avaliação ---

def test_avaliar_flag_desativada(cliente):
    cliente.post("/flags/", json={"name": "flag_off", "enabled": False})
    resposta = cliente.get("/flags/flag_off/evaluate?user_id=1")
    assert resposta.status_code == 200
    assert resposta.json()["enabled"] is False


def test_avaliar_flag_usuario_explicito(cliente):
    cliente.post("/flags/", json={"name": "flag_users", "enabled": True, "users": [42]})
    resposta = cliente.get("/flags/flag_users/evaluate?user_id=42")
    assert resposta.status_code == 200
    assert resposta.json()["enabled"] is True


def test_avaliar_flag_rollout_100_por_cento(cliente):
    cliente.post("/flags/", json={"name": "flag_full", "enabled": True, "rollout_percentage": 100})
    resposta = cliente.get("/flags/flag_full/evaluate?user_id=999")
    assert resposta.status_code == 200
    assert resposta.json()["enabled"] is True


def test_avaliar_flag_rollout_zero_por_cento(cliente):
    cliente.post("/flags/", json={"name": "flag_zero", "enabled": True, "rollout_percentage": 0})
    resposta = cliente.get("/flags/flag_zero/evaluate?user_id=999")
    assert resposta.status_code == 200
    assert resposta.json()["enabled"] is False


# --- Testes de atualização ---

def test_atualizar_flag(cliente):
    criacao = cliente.post("/flags/", json={"name": "flag_update", "enabled": False})
    flag_id = criacao.json()["id"]
    resposta = cliente.put(f"/flags/{flag_id}", json={"enabled": True})
    assert resposta.status_code == 200
    assert resposta.json()["enabled"] is True


def test_atualizar_flag_inexistente(cliente):
    resposta = cliente.put("/flags/9999", json={"enabled": True})
    assert resposta.status_code == 404


# --- Health check ---

def test_health_check(cliente):
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"
