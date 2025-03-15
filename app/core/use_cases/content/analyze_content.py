import json
from typing import List
from PIL import Image
from app.services.analyzer.text_analyzer import TextAnalyzer
from app.services.analyzer.image_analyzer import ImageAnalyzer
from app.services.ml.classifiers.llm_zeroshot_classification import (
    MultiModalClassificationAgent,
    TextClassificationAgent,
)
from app.adapters.repositories.template import TemplateRepository

from app.core.domain.models.analyze_response import AnalyzeResponse
from app.logger import logger
from app.configs import get_config, Config
from app.adapters.repositories.database import get_db


class AnalyzeContentUseCase:
    def __init__(
        self,
        text_analyzer: TextAnalyzer = None,
        image_analyzer: ImageAnalyzer = None,
        text_classifier: TextClassificationAgent = None,
        multimodal_classifier: MultiModalClassificationAgent = None,
        template_repository: TemplateRepository = None,
    ):
        self.text_analyzer = text_analyzer
        self.image_analyzer = image_analyzer
        self.text_classifier = text_classifier
        self.multimodal_classifier = multimodal_classifier
        self.template_repository = template_repository

    @staticmethod
    def from_config(config: Config = None):
        config = config or get_config()
        text_analyzer = TextAnalyzer.from_config(config)
        image_analyzer = ImageAnalyzer.from_config(config)
        text_classifier = TextClassificationAgent.from_config(config)
        multimodal_classifier = MultiModalClassificationAgent.from_config(config)
        template_repository = TemplateRepository(get_db())

        return AnalyzeContentUseCase(
            text_analyzer=text_analyzer,
            image_analyzer=image_analyzer,
            text_classifier=text_classifier,
            multimodal_classifier=multimodal_classifier,
            template_repository=template_repository,
        )

    async def process_content(
        self,
        texts: List[str],
        images: List[Image.Image] = None,
        pdf_files: List[str] = None,
        audio_files: List[str] = None,
        video_files: List[str] = None,
        gif_files: List[str] = None,
        extract_hyperlinks: bool = False,
        summarize_content: bool = False,
    ) -> AnalyzeResponse:
        """
        Process content for analysis

        Args:
            texts: List of text content to analyze
            images: List of image files to analyze
            pdf_files: List of PDF files to analyze
            audio_files: List of audio files to analyze
            video_files: List of video files to analyze
            gif_files: List of GIF files to analyze
            extract_hyperlinks: Whether to extract hyperlinks from text content
            summarize_content: Whether to summarize text content

        Returns:
            List of analysis results
        """
        metadata = {}
        summarization = ""
        logger.info("Processing content for analysis")

        # Process text content
        logger.info("Processing text content")
        for text in texts:
            text_result = await self.text_analyzer.analyze_text(
                content=text,
                extract_hyperlinks=extract_hyperlinks,
                summarize_content=summarize_content,
            )
            summarization += text_result.summary

        # Process image content
        lv1_categories = self.template_repository.get_by_level(1)
        self.lv1 = [
            category.name
            for category in lv1_categories
            if category.name not in ["Other", "Unknown"]
        ]
        if images:
            logger.info("Processing image content")
            # Do classification on text and images
            logger.info("Classifying content")
            content_category = await self.multimodal_classifier.classify_content(
                categories=self.lv1, texts=texts, images=images
            )
        else:
            content_category = await self.text_classifier.classify_content(
                texts=texts, categories=self.lv1
            )

        # check if content category has deeper level
        list_children = self.template_repository.get_by_parent_id(content_category.id)
        if list_children:
            self.lv2 = [category.name for category in list_children]
            content_category = await self.text_classifier.classify_content(
                texts=texts, categories=self.lv2
            )
            template_info = self.template_repository.get_by_name(content_category)
            if template_info:
                schema = template_info.schema
                metadata = {}
                for image in images:
                    metadata = await self.image_analyzer.analyze_image(
                        image=image, schema=schema
                    )

        return AnalyzeResponse(
            category=content_category,
            metadata=metadata,
            summarization=summarization,
        )
