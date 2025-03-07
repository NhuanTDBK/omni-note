# processors/image_processor.py
from openai import Client as LLMClient
from services import (
    ocr_service,
    classification_service,
    tag_service,
    embedding_service,
    agent_service,
    database_service,
)
from app.logger import logger


class ImageDetector:
    def __init__(self, client: LLMClient):
        self.client = client

    def process_image(file):
        """
        Process uploaded images

        Args:
            file: The uploaded image file

        Returns:
            dict: Processing result with metadata
        """
        # Classify image type
        image_type = classification_service.classify_image(file)

        # Extract text via OCR
        extracted_text = ocr_service.extract_text_from_image(file)

        # Generate image tags
        tags = tag_service.generate_image_tags(file, extracted_text, image_type)

        # Generate embeddings for both the image and extracted text
        image_embedding = embedding_service.generate_image_embedding(file)
        text_embedding = embedding_service.generate_text_embeddings(extracted_text)

        # Get schema for structured data extraction based on image type
        schema = database_service.get_schema_for_type(image_type)

        # Extract structured data using the schema
        structured_data = agent_service.extract_structured_data(
            image=file, text=extracted_text, schema=schema
        )

        # Store in database
        image_id = database_service.store_image(
            filename=file.filename,
            image_type=image_type,
            extracted_text=extracted_text,
            structured_data=structured_data,
            tags=tags,
            image_embedding=image_embedding,
            text_embedding=text_embedding,
        )

        return {
            "id": image_id,
            "filename": file.filename,
            "image_type": image_type,
            "extracted_text": extracted_text,
            "structured_data": structured_data,
            "tags": tags,
        }
