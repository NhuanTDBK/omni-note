from typing import List, Optional
from sqlalchemy.orm import Session
from app.adapters.persistance.tag import Tag


class TagRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, tag: Tag) -> Tag:
        """Create a new tag"""
        self.session.add(tag)
        self.session.commit()
        return tag

    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """Get a tag by its ID"""
        return self.session.query(Tag).filter(Tag.tag_id == tag_id).first()

    def get_by_material_id(self, material_id: str) -> List[Tag]:
        """Get all tags for a specific material"""
        return self.session.query(Tag).filter(Tag.material_id == material_id).all()

    def get_all(self) -> List[Tag]:
        """Get all tags"""
        return self.session.query(Tag).all()

    def update(self, tag: Tag) -> Tag:
        """Update an existing tag"""
        existing_tag = self.get_by_id(tag.tag_id)
        if existing_tag:
            existing_tag.material_id = tag.material_id
            existing_tag.tag_type = tag.tag_type
            existing_tag.tag_value = tag.tag_value
            existing_tag.confidence = tag.confidence
            self.session.commit()
        return existing_tag

    def delete(self, tag_id: int) -> bool:
        """Delete a tag by its ID"""
        tag = self.get_by_id(tag_id)
        if tag:
            self.session.delete(tag)
            self.session.commit()
            return True
        return False
