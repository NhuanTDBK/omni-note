import os
import json
from typing import List
from openai import Client
from fastapi import APIRouter, UploadFile

from app.config import get_settings
from app.agent.classification import ClassificationAgent
from app.agent.extractor import MetadataExtractor


router = APIRouter()
settings = get_settings()

agent_classify = ClassificationAgent(
    client=Client(
        api_key=settings.AGENT_CATEGORIZATION_LLM_API_KEY,
        base_url=settings.AGENT_CATEGORIZATION_LLM_URL,
    ),
    model_id=settings.AGENT_CATEGORIZATION_LLM_MODEL,
    categories=json.load(open("app/material_schema/lv1/schema.json"))["subcategories"],
)


@router.post("/extract_data")
async def extract_data(texts: List[str], files: List[UploadFile]):
    """Upload a new document"""

    images = [file.file.read() for file in files]
    category = agent_classify.classify_content(
        texts=texts,
        images=images,
    )

    schema_path = "app/material_schema/lv2/{}.json".format(
        category.lower().replace(" ", "_").replace(">", "/")
    )
    schema = {}
    metadata = {}
    if os.path.exists(schema_path):
        agent_extract = MetadataExtractor(
            client=Client(
                api_key=settings.AGENT_EXTRACTOR_LLM_API_KEY,
                base_url=settings.AGENT_EXTRACTOR_LLM_URL,
            ),
            model_id=settings.AGENT_EXTRACTOR_LLM_MODEL,
            schema=schema,
        )
        metadata = agent_extract.extract_metadata(
            texts=texts,
            images=images,
        )

    return {"category": category, "metadata": metadata}
