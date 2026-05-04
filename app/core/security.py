from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import configuracoes

ALGORITMO = "HS256"
EXPIRACAO_TOKEN_HORAS = 24

bearer_scheme = HTTPBearer(auto_error=False)


def criar_token(dados: dict, expira_em: Optional[timedelta] = None) -> str:
    """Cria um JWT com os dados fornecidos."""
    payload = dados.copy()
    expiracao = datetime.now(timezone.utc) + (expira_em or timedelta(hours=EXPIRACAO_TOKEN_HORAS))
    payload["exp"] = expiracao
    return jwt.encode(payload, configuracoes.secret_key, algorithm=ALGORITMO)


def verificar_token(token: str) -> dict:
    """Decodifica e valida um JWT."""
    try:
        return jwt.decode(token, configuracoes.secret_key, algorithms=[ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


def exigir_admin(
    credenciais: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    """Dependência que exige um token JWT com papel 'admin'."""
    if not credenciais:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token não fornecido")
    payload = verificar_token(credenciais.credentials)
    if payload.get("papel") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado: requer papel admin")
    return payload
