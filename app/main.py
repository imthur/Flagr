import logging

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers.feature_flag_router import router as router_flags

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Feature Flags API",
    description=(
        "API para gerenciamento de feature flags com suporte a rollout percentual, "
        "ativação por usuário e cache Redis."
    ),
    version="1.0.0",
)

app.include_router(router_flags)


@app.get("/health", tags=["Saúde"], summary="Verificação de saúde")
def health_check() -> dict:
    """Confirma que a API está no ar."""
    return {"status": "ok"}
