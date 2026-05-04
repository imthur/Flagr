from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.feature_flag import FeatureFlag
from app.schemas.feature_flag import FeatureFlagCriar, FeatureFlagAtualizar


class FeatureFlagRepository:
    """Repositório responsável exclusivamente pelo acesso ao banco de dados."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(self, dados: FeatureFlagCriar) -> FeatureFlag:
        """Persiste uma nova feature flag no banco."""
        flag = FeatureFlag(**dados.model_dump())
        self.db.add(flag)
        self.db.commit()
        self.db.refresh(flag)
        return flag

    def listar(self) -> List[FeatureFlag]:
        """Retorna todas as feature flags cadastradas."""
        return self.db.query(FeatureFlag).all()

    def buscar_por_nome(self, nome: str) -> Optional[FeatureFlag]:
        """Busca uma feature flag pelo seu nome único."""
        return self.db.query(FeatureFlag).filter(FeatureFlag.name == nome).first()

    def buscar_por_id(self, flag_id: int) -> Optional[FeatureFlag]:
        """Busca uma feature flag pelo seu ID."""
        return self.db.query(FeatureFlag).filter(FeatureFlag.id == flag_id).first()

    def atualizar(self, flag_id: int, dados: FeatureFlagAtualizar) -> Optional[FeatureFlag]:
        """Atualiza os campos fornecidos de uma feature flag."""
        flag = self.buscar_por_id(flag_id)
        if not flag:
            return None
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(flag, campo, valor)
        self.db.commit()
        self.db.refresh(flag)
        return flag

    def deletar(self, flag_id: int) -> bool:
        """Remove uma feature flag do banco. Retorna True se deletada."""
        flag = self.buscar_por_id(flag_id)
        if not flag:
            return False
        self.db.delete(flag)
        self.db.commit()
        return True
