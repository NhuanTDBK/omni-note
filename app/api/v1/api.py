from fastapi import APIRouter
from app.api.v1.endpoints import documents
from app.api.v1.endpoints import embeddings

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(embeddings.router, prefix="/embeddings", tags=["embeddings"])
