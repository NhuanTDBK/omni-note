from typing import List, Optional, Annotated
from io import BytesIO
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.use_cases.content.analyze_content import AnalyzeContentUseCase
from app.core.use_cases.search.search_content import SearchContentUseCase
from app.configs import get_config

from app.adapters.repositories.material import MaterialRepository
from app.adapters.persistance.material import MaterialContent
from app.api.deps import get_db, get_current_user
from app.api.v1.schema.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    MaterialListResponse,
    ExtractDataResponse,
)

router = APIRouter()
config = get_config()
content_usecase = AnalyzeContentUseCase.from_config(config=config)
search_usecase = SearchContentUseCase.from_config(config=config)


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    material: MaterialCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not material.title or not material.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and content are required",
        )

    repo = MaterialRepository(db)
    new_material = MaterialContent(
        user_id=current_user,
        title=material.title,
        content=material.content.encode("utf-8") if material.content else None,
        metadata_data=material.metadata_data if material.metadata_data else None,
    )
    inserted_material = repo.create(new_material)
    return MaterialResponse(status=True)


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = MaterialRepository(db)
    material = repo.get(material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material not found"
        )
    if material.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this material",
        )
    return material


@router.get("/all/", response_model=MaterialListResponse)
async def list_materials(
    current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    repo = MaterialRepository(db)
    items = repo.list(current_user)
    return MaterialListResponse(total=len(items), items=items)


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: UUID,
    material: MaterialUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not material.title or not material.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and content are required",
        )

    repo = MaterialRepository(db)
    existing = repo.get(material_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material not found"
        )
    if existing.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this material",
        )

    existing.title = material.title
    existing.content = material.content
    existing.tags = material.tags
    return repo.update(existing)


@router.delete("/{material_id}")
async def delete_material(
    material_id: UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = MaterialRepository(db)
    existing = repo.get(material_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material not found"
        )
    if existing.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this material",
        )

    repo.delete(material_id)
    return {"message": "Material deleted successfully"}


@router.post("/extract_data", response_model=ExtractDataResponse)
async def extract_data(
    texts: Optional[List[str]] = [],
    files: Annotated[List[UploadFile], File()] = None,
    lang: Optional[str] = "en_us",
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a new content"""
    # Process files
    if not files:
        files = []

    images: List[bytes] = []
    for file in files:
        content = await file.read()
        mimetype = file.content_type

        if "image" in mimetype:
            # Process image file
            images.append(content)

    images = [Image.open(BytesIO(image)) for image in images]
    # convert to PIL Image

    response = await content_usecase.process_content(
        texts=texts,
        images=images,
        summarize_content=True,
        extract_hyperlinks=True,
    )

    return ExtractDataResponse(
        category=response.category,
        summarization=response.summarization,
        metadata=response.metadata,
        user_id=current_user,
    )


@router.post("/search")
async def search(
    query: str,
    limit: int = 10,
):
    results = await search_usecase.search(query=query, limit=limit)
    return results
