from pydantic_settings import BaseSettings


class Configuracoes(BaseSettings):
    """Configurações da aplicação carregadas do arquivo .env."""

    database_url: str
    redis_host: str
    redis_port: int = 6379
    secret_key: str

    class Config:
        env_file = ".env"


configuracoes = Configuracoes()
