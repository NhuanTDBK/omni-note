from PIL import Image
from app.services.ml.ocr.paddle_paddle import PaddleOCRModel
from app.services.ml.extractors.json_structure import (
    JsonStructureExtractor,
    MultiModalJsonStructureExtractor,
)
from app.configs import Config


class PaddleOCRImageAnalyzer:
    def __init__(
        self,
        ocr_service: PaddleOCRModel = None,
        structure_extractor_service: JsonStructureExtractor = None,
    ):
        self.ocr_service = ocr_service
        self.structure_extractor_service = structure_extractor_service

    @staticmethod
    def from_config(config: Config):
        ocr_service = PaddleOCRModel.from_config(config)
        structure_extractor_service = JsonStructureExtractor.from_config(config)
        return PaddleOCRImageAnalyzer(
            ocr_service=ocr_service,
            structure_extractor_service=structure_extractor_service,
        )

    async def analyze_image(self, image: Image.Image, schema: dict) -> dict:
        """
        Analyze an image and extract structured metadata
        Args:
            image: The image to analyze
        Returns:
            A dictionary containing the structured metadata extracted from the image
        """
        # Perform OCR on the image
        ocr_results = self.ocr_service.predict(image)

        # Extract structured metadata from the OCR results
        structured_metadata = await self.structure_extractor_service.extract_metadata(
            schema=schema, texts=ocr_results
        )

        return structured_metadata


class LLMOCRImageAnalyzer:
    def __init__(
        self,
        structure_extractor_service: MultiModalJsonStructureExtractor = None,
    ):
        self.structure_extractor_service = structure_extractor_service

    @staticmethod
    def from_config(config: Config):
        structure_extractor_service = MultiModalJsonStructureExtractor.from_config(
            config
        )
        return LLMOCRImageAnalyzer(
            structure_extractor_service=structure_extractor_service,
        )

    async def analyze_image(self, image: Image.Image, schema: dict) -> dict:
        """
        Analyze an image and extract structured metadata
        Args:
            image: The image to analyze
        Returns:
            A dictionary containing the structured metadata extracted from the image
        """

        # Extract structured metadata from the OCR results
        structured_metadata = await self.structure_extractor_service.extract_metadata(
            schema=schema, texts=[], images=[image]
        )

        return structured_metadata
