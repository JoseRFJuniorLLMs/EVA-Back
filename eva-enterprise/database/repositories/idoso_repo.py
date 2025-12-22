from sqlalchemy.orm import Session
from ..models import Idoso, Familiar, LegadoDigital
from typing import List, Optional

class IdosoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Idoso]:
        return self.db.query(Idoso).offset(skip).limit(limit).all()

    def get_by_id(self, idoso_id: int) -> Optional[Idoso]:
        return self.db.query(Idoso).filter(Idoso.id == idoso_id).first()

    def get_by_telefone(self, telefone: str) -> Optional[Idoso]:
        return self.db.query(Idoso).filter(Idoso.telefone == telefone).first()

    def create(self, dados: dict) -> Idoso:
        idoso = Idoso(**dados)
        self.db.add(idoso)
        self.db.commit()
        self.db.refresh(idoso)
        return idoso

    def update(self, idoso_id: int, dados: dict) -> Optional[Idoso]:
        idoso = self.get_by_id(idoso_id)
        if idoso:
            for k, v in dados.items():
                if v is not None:
                    setattr(idoso, k, v)
            self.db.commit()
            self.db.refresh(idoso)
        return idoso

    def delete(self, idoso_id: int) -> bool:
        idoso = self.get_by_id(idoso_id)
        if idoso:
            self.db.delete(idoso)
            self.db.commit()
            return True
        return False

    # Familiares
    def get_familiares(self, idoso_id: int) -> List[Familiar]:
        return self.db.query(Familiar).filter(Familiar.idoso_id == idoso_id).all()

    def add_familiar(self, idoso_id: int, dados: dict) -> Familiar:
        familiar = Familiar(idoso_id=idoso_id, **dados)
        self.db.add(familiar)
        self.db.commit()
        self.db.refresh(familiar)
        return familiar

    def update_familiar(self, familiar_id: int, dados: dict) -> Optional[Familiar]:
        familiar = self.db.query(Familiar).filter(Familiar.id == familiar_id).first()
        if familiar:
            for k, v in dados.items():
                if v is not None:
                    setattr(familiar, k, v)
            self.db.commit()
            self.db.refresh(familiar)
        return familiar

    # Legado Digital
    def get_legado(self, idoso_id: int) -> List[LegadoDigital]:
        return self.db.query(LegadoDigital).filter(LegadoDigital.idoso_id == idoso_id).all()

    def add_legado(self, idoso_id: int, dados: dict) -> LegadoDigital:
        item = LegadoDigital(idoso_id=idoso_id, **dados)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove_legado(self, item_id: int) -> bool:
        item = self.db.query(LegadoDigital).filter(LegadoDigital.id == item_id).first()
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False
