from pydantic_settings import BaseSettings


class Configuracoes(BaseSettings):
    """Configurações da aplicação carregadas do arquivo .env."""

    database_url: str
    redis_url: str
    secret_key: str

    class Config:
        env_file = ".env"


configuracoes = Configuracoes()
