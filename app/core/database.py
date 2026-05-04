from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from typing import Generator
from app.core.config import configuracoes


engine = create_engine(configuracoes.database_url)
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def obter_db() -> Generator[Session, None, None]:
    """Dependência que fornece uma sessão de banco de dados."""
    db = SessaoLocal()
    try:
        yield db
    finally:
        db.close()
