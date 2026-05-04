from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class FeatureFlag(Base):
    """Modelo de banco de dados para feature flags."""

    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    rollout_percentage = Column(Integer, nullable=True)
    users = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
