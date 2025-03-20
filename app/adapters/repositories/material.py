from typing import List, Optional
from sqlalchemy.orm import Session
from app.adapters.persistance.material import MaterialContent


class MaterialRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, material: MaterialContent) -> MaterialContent:
        self.session.add(material)
        self.session.commit()
        return material

    def get(self, material_id: str) -> Optional[MaterialContent]:
        return (
            self.session.query(MaterialContent)
            .filter(MaterialContent.id == material_id)
            .first()
        )

    def list(self, user_id: str) -> List[MaterialContent]:
        return (
            self.session.query(MaterialContent)
            .filter(MaterialContent.user_id == user_id)
            .all()
        )

    def update(self, material: MaterialContent) -> MaterialContent:
        existing = self.get(material.id)
        if existing:
            for key, value in material.__dict__.items():
                if not key.startswith("_"):
                    setattr(existing, key, value)
            self.session.commit()
        return existing

    def delete(self, material_id: str) -> bool:
        material = self.get(material_id)
        if material:
            self.session.delete(material)
            self.session.commit()
            return True
        return False
