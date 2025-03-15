from typing import List, Optional, Annotated

from fastapi import APIRouter, UploadFile, File, Form

from app.core.use_cases.content.analyze_content import AnalyzeContentUseCase
from app.configs import get_config
from app.logger import logger


router = APIRouter()
config = get_config()
content_usecase = AnalyzeContentUseCase.from_config(config=config)


@router.post("/extract_data")
async def extract_data(
    texts: List[str] = Form(...),
    files: Annotated[List[UploadFile], File()] = None,
    lang: Optional[str] = "en_us",
):
    """Upload a new content"""
    # Process files
    if not files:
        files = []

    images = []
    for file in files:
        content = await file.read()
        mimetype = file.content_type

        if "image" in mimetype:
            # Process image file
            images.append(content)

    response = await content_usecase.process_content(
        texts=texts,
        images=images,
        summarize_content=True,
        extract_hyperlinks=True,
    )

    return response
