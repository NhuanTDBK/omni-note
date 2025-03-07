from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection_name = "documents"
        self.vector_size = 768  # Default for many embedding models
    
    async def init_collection(self):
        """Initialize the vector collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )
    
    async def search(self, query_vector, limit=10):
        """Search for similar vectors"""
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
