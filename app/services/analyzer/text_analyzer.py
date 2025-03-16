import re
import asyncio

from app.services.web.base_crawler import CrawlerService
from app.services.web.crawler_service import AsyncRequestCrawlerService
from app.services.ml.embedding.visual_colpali import VisualModelEmbedding
from app.services.ml.summarization import ContentSummarizer
from app.configs import Config


class TextAnalyzerResponse:
    def __init__(self, hyperlinks=None, summary=None):
        self.hyperlinks = hyperlinks
        self.summary = summary

    def to_dict(self):
        return {
            "hyperlinks": self.hyperlinks,
            "summary": self.summary,
        }


class TextAnalyzer:
    def __init__(
        self,
        web_crawler_service: CrawlerService = None,
        visual_model_embedding: VisualModelEmbedding = None,
        content_summarizer: ContentSummarizer = None,
    ):
        self.web_crawler_service = web_crawler_service
        self.visual_model_embedding = visual_model_embedding
        self.content_summarizer = content_summarizer
        self.url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )

    @staticmethod
    def from_config(config: Config):
        web_crawler_service = AsyncRequestCrawlerService.from_config(config)
        # visual_model_embedding = VisualModelEmbedding.from_config(config)
        content_summarizer = ContentSummarizer.from_config(config)
        return TextAnalyzer(
            web_crawler_service=web_crawler_service,
            # visual_model_embedding=visual_model_embedding,
            content_summarizer=content_summarizer,
        )

    def extract_hyperlinks(self, content: str):
        """
        Extract hyperlinks from text content

        Args:
            content: The text content to extract hyperlinks from

        Returns:
            A list of hyperlinks
        """
        # Extract hyperlinks from content

        urls = re.findall(self.url_pattern, content)
        return urls

    async def analyze_text(
        self,
        content: str,
        extract_hyperlinks: bool = False,
        summarize_content: bool = False,
    ) -> TextAnalyzerResponse:
        """
        Analyze text content

        Args:
            content: The text content to analyze
            extract_hyperlinks: Whether to extract hyperlinks from the content
            summarize_content: Whether to summarize the content

        Returns:
            A dictionary with the analysis results
        """
        analysis_results = {}

        if extract_hyperlinks:
            hyperlinks = self.extract_hyperlinks(content)
            analysis_results["hyperlinks"] = hyperlinks
            # Fetch content from hyperlinks simultaneously by asyncio gather
            tasks = [
                asyncio.create_task(self.web_crawler_service.extract_content(url))
                for url in hyperlinks
            ]
            hyperlinks_content = await asyncio.gather(*tasks)
            formatted_content = "\n".join(
                [
                    f"Title: {title}\nContent: {content}"
                    for title, content in hyperlinks_content
                ]
            )
            content = """
                # Original User note
                {}
                # Extracted hyperlinks content
                Here are the extracted hyperlinks content that we found in the note: 
                {}
                """.format(
                content, formatted_content
            )

        if summarize_content:
            summary = await self.content_summarizer.summarize_content(content)
            analysis_results["summary"] = summary

        return TextAnalyzerResponse(**analysis_results)
