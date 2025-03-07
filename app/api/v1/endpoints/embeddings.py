from typing import List, Any
from PIL import Image

import orjson
import torch

from fastapi import APIRouter, UploadFile, Response
from transformers.utils.import_utils import is_flash_attn_2_available
from colpali_engine.models import ColQwen2, ColQwen2Processor

from app.config import get_settings

router = APIRouter()
config = get_settings()

print(f"Loading model {config.EMBEDDING_MODEL}...")

device = "cpu"
if torch.cuda.is_available():
    device = "cuda"
if torch.mps.is_available():
    device = "mps"

torch_dtype = torch.float16
if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
    torch_dtype = torch.bfloat16

# model = ColQwen2.from_pretrained(
#     config.EMBEDDING_MODEL,
#     torch_dtype=torch_dtype,
#     device_map=device,  # or "mps" if on Apple Silicon
#     attn_implementation="flash_attention_2" if is_flash_attn_2_available() else None,
# ).eval()

processor = ColQwen2Processor.from_pretrained(config.EMBEDDING_MODEL)


class VectorJsonResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(
            content,
            option=orjson.OPT_SERIALIZE_NUMPY,
        )


@router.post("/image_embedding")
async def get_image_embedding(files: List[UploadFile]):
    images = [Image.open(file.file) for file in files]
    batch_images = processor.process_images(images).to(model.device)
    with torch.no_grad():
        image_embeddings = model(**batch_images).detach().cpu().numpy()
        return VectorJsonResponse(
            content={
                "image_embeddings": image_embeddings,
                "shape": image_embeddings.shape,
            }
        )


@router.post("/query_embedding")
async def get_query_embedding(
    queries: List[str],
):
    batch_queries = processor.process_queries(queries).to(model.device)
    with torch.no_grad():
        query_embeddings = model(**batch_queries).detach().cpu().numpy()
        return VectorJsonResponse(
            content={
                "query_embeddings": query_embeddings,
                "shape": query_embeddings.shape,
            },
        )