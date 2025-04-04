from typing import List

from app.adapters.repositories.material import MaterialRepository
from app.core.domain.models.search_response import SearchResponse
from app.services.ml.embedding.visual_colpali import VisualModelEmbedding
from app.configs import get_config, Config
from app.adapters.repositories.database import get_db, get_qdrant_client
from app.logger import logger


class SearchContentUseCase:
    def __init__(
        self,
        embedding_repository: VisualModelEmbedding = None,
        content_repository: MaterialRepository = None,
    ):
        self.embedding_repository = embedding_repository
        self.content_repository = content_repository

    @staticmethod
    def from_config(config: Config = None):
        config = config or get_config()
        db = get_db()
        qdrant_client = get_qdrant_client()
        embedding_repository = VisualModelEmbedding.from_config(config=config)
        content_repository = MaterialRepository(session=db, qdrant_client=qdrant_client)

        return SearchContentUseCase(
            embedding_repository=embedding_repository,
            content_repository=content_repository,
        )

    async def search(self, query: str, limit: int = 10) -> List[SearchResponse]:
        """
        Search for content based on query string using vector similarity

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of Content objects matching the query
        """
        logger.info(f"Searching content with query: {query}")

        # Get query embedding
        query_embedding = self.embedding_repository.get_texts_embedding(query)
        query_embedding = query_embedding[0].tolist()

        # Search similar content
        content_scores = await self.content_repository.semantic_search(
            vector=query_embedding, limit=limit
        )
        if not content_scores:
            return []
        content_scores = content_scores.points

        # Convert to MaterialContent objects
        id_scores = {content.id: content.score for content in content_scores}
        contents = self.content_repository.get_by_ids(ids=list(id_scores.keys()))

        result = [
            {"id": content.id, "score": id_scores[content.id], "payload": contents[i]}
            for i, content in enumerate(contents)
        ]

        result = sorted(result, key=lambda x: x["score"], reverse=True)

        return result
