from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adapters.persistance.template import Template
from app.adapters.repositories.template import TemplateRepository
from app.api.deps import get_db
from app.api.v1.schema.template import TemplateCreate, TemplateResponse, TemplateUpdate

router = APIRouter()


@router.post("/templates/", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    template_repo = TemplateRepository(db)
    db_template = Template(
        name=template.name,
        level=template.level,
        parent_id=template.parent_id,
        content=template.content,
    )
    return template_repo.create(db_template)


@router.get("/templates/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template_repo = TemplateRepository(db)
    template = template_repo.get_by_id(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.get("/templates/level/{level}", response_model=List[TemplateResponse])
def get_templates_by_level(level: int, db: Session = Depends(get_db)):
    template_repo = TemplateRepository(db)
    return template_repo.get_by_level(level)


@router.get("/templates/parent/{parent_id}", response_model=List[TemplateResponse])
def get_templates_by_parent(parent_id: int, db: Session = Depends(get_db)):
    template_repo = TemplateRepository(db)
    return template_repo.get_by_parent_id(parent_id)


@router.put("/templates/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int, template: TemplateUpdate, db: Session = Depends(get_db)
):
    template_repo = TemplateRepository(db)
    db_template = Template(
        id=template_id,
        name=template.name,
        level=template.level,
        parent_id=template.parent_id,
        content=template.content,
    )
    updated_template = template_repo.update(db_template)
    if updated_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return updated_template


@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template_repo = TemplateRepository(db)
    if not template_repo.delete(template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}
