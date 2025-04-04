from typing import List, Optional
from sqlalchemy.orm import Session
from qdrant_client import AsyncQdrantClient, models
from app.adapters.persistance.material import MaterialContent


class MaterialRepository:
    def __init__(self, session: Session, qdrant_client: AsyncQdrantClient = None):
        self.session = session
        self.qdrant_client = qdrant_client

    def create(self, material: MaterialContent) -> MaterialContent:
        self.session.add(material)
        self.session.commit()
        return material

    def get(self, material_id: str) -> Optional[MaterialContent]:
        return (
            self.session.query(MaterialContent)
            .filter(MaterialContent.id == material_id)
            .first()
        )

    def list(self, user_id: str) -> List[MaterialContent]:
        return (
            self.session.query(MaterialContent)
            .filter(MaterialContent.user_id == user_id)
            .all()
        )

    def update(self, material: MaterialContent) -> MaterialContent:
        existing = self.get(material.id)
        if existing:
            for key, value in material.__dict__.items():
                if not key.startswith("_"):
                    setattr(existing, key, value)
            self.session.commit()
        return existing

    def delete(self, material_id: str) -> bool:
        material = self.get(material_id)
        if material:
            self.session.delete(material)
            self.session.commit()
            return True
        return False

    async def semantic_search(self, vector: List[float], limit: int = 10):
        """
        Search for templates using Qdrant
        Args:
            vector: The vector to search for
            limit: The maximum number of results to return
        Returns:
            A list of templates matching the search criteria

        """
        # Perform search using Qdrant
        results = await self.qdrant_client.query_points(
            collection_name="ai_search",
            query=vector,
            limit=limit,
            timeout=60,
            with_payload=False,
            with_vectors=False,
            search_params=models.SearchParams(
                quantization=models.QuantizationSearchParams(
                    ignore=False,
                    rescore=True,
                    oversampling=2.0,
                )
            ),
        )
        return results

    def get_by_ids(self, ids: List[str]) -> List[MaterialContent]:
        """
        Get materials by their IDs
        Args:
            ids: The list of material IDs
        Returns:
            A list of materials with the specified IDs
        """
        return (
            self.session.query(MaterialContent)
            .filter(MaterialContent.id.in_(ids))
            .all()
        )
