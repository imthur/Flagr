import logging

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers.feature_flag_router import router as router_flags

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

description = """
Gerencie **feature flags** com rollout gradual, ativação por usuário e cache Redis.

## O que você pode fazer

- **Criar flags** com nome único e configurar o comportamento de ativação
- **Rollout percentual** — ative a flag para X% dos usuários de forma determinística
- **Ativação por usuário** — liste IDs específicos que sempre terão a flag ativa
- **Avaliar em tempo real** — consulte se uma flag está ativa para um `user_id`
- **Cache automático** — respostas cacheadas no Redis por 5 minutos

## Como a avaliação funciona

Ao chamar `/flags/{nome}/evaluate?user_id=42`, a API segue esta ordem:

1. Flag desativada → `false`
2. Usuário está na lista explícita → `true`
3. Rollout percentual (hash determinístico) → `true` ou `false`
4. Fallback para o estado global da flag
"""

app = FastAPI(
    title="Flagr",
    description=description,
    version="1.0.0",
)

app.include_router(router_flags)


@app.get("/", tags=["Geral"], summary="Bem-vindo")
def root() -> dict:
    return {
        "app": "Flagr",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Geral"], summary="Verificação de saúde")
def health_check() -> dict:
    return {"status": "ok"}
