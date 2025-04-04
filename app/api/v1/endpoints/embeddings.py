from typing import List, Any
from PIL import Image

import orjson

from fastapi import APIRouter, UploadFile, Response
from app.configs import get_config
from app.services.ml.embedding.visual_colpali import VisualModelEmbedding

router = APIRouter()
config = get_config()


class VectorJsonResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(
            content,
            option=orjson.OPT_SERIALIZE_NUMPY,
        )


# processor = VisualModelEmbedding(config.EMBEDDING_MODEL)


@router.post("/image_embedding")
async def get_image_embedding(files: List[UploadFile]):
    images = [Image.open(file.file) for file in files]
    image_embeddings = processor.get_images_embedding(images)
    return VectorJsonResponse(
        content={
            "image_embeddings": image_embeddings,
            "shape": image_embeddings.shape,
        }
    )


@router.post("/text_embedding")
async def get_query_embedding(
    queries: List[str],
):
    query_embeddings = processor.get_texts_embedding(queries)
    return VectorJsonResponse(
        content={
            "query_embeddings": query_embeddings,
            "shape": query_embeddings.shape,
        },
    )
