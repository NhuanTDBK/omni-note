from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adapters.persistance.tag import Tag
from app.adapters.repositories.tag import TagRepository
from app.api.deps import get_db, get_current_user
from app.api.v1.schema.tag import TagCreate, TagResponse, TagUpdate

router = APIRouter()


@router.post("/tags/", response_model=TagResponse)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    tag_repo = TagRepository(db)
    db_tag = Tag(
        material_id=tag.material_id,
        tag_type=tag.tag_type,
        tag_value=tag.tag_value,
        confidence=tag.confidence,
    )
    return tag_repo.create(db_tag)


@router.get("/tags/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag_repo = TagRepository(db)
    tag = tag_repo.get_by_id(tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/tags/material/{material_id}", response_model=List[TagResponse])
def get_tags_by_material(material_id: str, db: Session = Depends(get_db)):
    tag_repo = TagRepository(db)
    return tag_repo.get_by_material_id(material_id)


@router.get("/tags/", response_model=List[TagResponse])
def get_all_tags(db: Session = Depends(get_db)):
    tag_repo = TagRepository(db)
    return tag_repo.get_all()


@router.put("/tags/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    tag_repo = TagRepository(db)
    db_tag = Tag(
        tag_id=tag_id,
        material_id=tag.material_id,
        tag_type=tag.tag_type,
        tag_value=tag.tag_value,
        confidence=tag.confidence,
    )
    updated_tag = tag_repo.update(db_tag)
    if updated_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return updated_tag


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag_repo = TagRepository(db)
    if not tag_repo.delete(tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"message": "Tag deleted successfully"}
