import re
import os
import json
from typing import List, Optional, Annotated

from openai import AsyncClient
from fastapi import APIRouter, UploadFile, File, Form

# from app.logger import logger
from app.config import get_settings
from app.agent.classification import ClassificationAgent
from app.agent.extractor import MetadataExtractor
from app.agent.summarization import ContentSummarizer
from app.processor.web_processor import WebProcessor

import logging

logger = logging.getLogger(__name__)

# import cv2
# from PIL import Image
# import tempfile
# import io
# import fitz  # PyMuPDF


router = APIRouter()
settings = get_settings()


agent_classify = ClassificationAgent(
    client=AsyncClient(
        api_key=settings.AGENT_CATEGORIZATION_LLM_API_KEY,
        base_url=settings.AGENT_CATEGORIZATION_LLM_URL,
    ),
    model_id=settings.AGENT_CATEGORIZATION_LLM_MODEL,
    categories=json.load(open("app/material_schema/lv1/schema.json"))["subcategories"],
)
web_processor = WebProcessor()


@router.post("/extract_data")
async def extract_data(
    texts: List[str] = Form(...),
    files: Annotated[List[UploadFile], File()] = None,
    lang: Optional[str] = "en_us",
):
    """Upload a new document"""

    # Process texts for any URLs

    processed_texts = []
    images = []

    metadata = {}
    category = ""
    # Check texts for links and download content
    for text in texts:
        processed_texts.append(text)
        # Find URLs in the text
        url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )
        urls = re.findall(url_pattern, text)
        for i, url in enumerate(urls):
            try:
                content = await web_processor.extract_content(url)
                processed_texts.append(
                    "# URL Content {}\n #Title: {}\n #Content: {}".format(
                        i + 1, content[0], content[1]
                    )
                )
            except Exception as e:
                logger.error(f"Error downloading content: {e}")
        text = "\n".join(processed_texts)
        agent_summarizer = ContentSummarizer(
            client=AsyncClient(
                api_key=settings.AGENT_SUMMARIZATION_LLM_API_KEY,
                base_url=settings.AGENT_SUMMARIZATION_LLM_URL,
            ),
            model_id=settings.AGENT_SUMMARIZATION_LLM_MODEL,
            lang=lang,
        )
        summary = await agent_summarizer.summarize_content(text)
        metadata["summary"] = summary

    # Process files
    if not files:
        files = []

    images = []
    for file in files:
        content = await file.read()
        mimetype = file.content_type

        if "image" in mimetype:
            # Process image file
            images.append(content)
        # elif mimetype == 'application/pdf':
        #     # Convert PDF to images
        #     with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        #         temp_pdf.write(content)
        #         temp_pdf_path = temp_pdf.name

        #     try:
        #         pdf_document = fitz.open(temp_pdf_path)
        #         for page_num in range(len(pdf_document)):
        #             page = pdf_document.load_page(page_num)
        #             pix = page.get_pixmap()
        #             img_data = pix.tobytes()
        #             images.append(img_data)
        #         pdf_document.close()
        #         os.unlink(temp_pdf_path)
        #     except Exception as e:
        #         print(f"Error processing PDF: {e}")
        # elif mimetype == 'image/gif':
        #     # Convert GIF to images (extract all frames)
        #     try:
        #         with Image.open(io.BytesIO(content)) as gif:
        #             frame_count = getattr(gif, 'n_frames', 1)
        #             for frame_idx in range(frame_count):
        #                 gif.seek(frame_idx)
        #                 frame = gif.convert('RGB')
        #                 img_byte_arr = io.BytesIO()
        #                 frame.save(img_byte_arr, format='PNG')
        #                 images.append(img_byte_arr.getvalue())
        #     except Exception as e:
        #         print(f"Error processing GIF: {e}")
        # elif mimetype == 'video/mp4':
        #     # Extract frames from video
        #     try:
        #         with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
        #             temp_video.write(content)
        #             temp_video_path = temp_video.name

        #         cap = cv2.VideoCapture(temp_video_path)
        #         # Extract a frame every second
        #         fps = cap.get(cv2.CAP_PROP_FPS)
        #         frame_interval = int(fps)
        #         frame_count = 0

        #         while cap.isOpened():
        #             ret, frame = cap.read()
        #             if not ret:
        #                 break

        #             if frame_count % frame_interval == 0:
        #                 success, buffer = cv2.imencode(".jpg", frame)
        #                 if success:
        #                     images.append(buffer.tobytes())

        #             frame_count += 1

        #         cap.release()
        #         os.unlink(temp_video_path)
        #     except Exception as e:
        #         print(f"Error processing video: {e}")
        elif "text" in mimetype:
            # Add text content to texts
            processed_texts.append(content.decode("utf-8", errors="ignore"))

    # Update texts with processed texts
    text = "\n".join(processed_texts)

    if len(images) > 0:
        category = await agent_classify.classify_content(
            texts=texts,
            images=images,
        )

        schema_path = "app/material_schema/lv2/{}.json".format(
            category.lower().replace(" ", "_").replace(">", "/")
        )
        schema = {}
        metadata = {}
        if os.path.exists(schema_path):
            agent_extract = MetadataExtractor(
                client=AsyncClient(
                    api_key=settings.AGENT_EXTRACTOR_LLM_API_KEY,
                    base_url=settings.AGENT_EXTRACTOR_LLM_URL,
                ),
                model_id=settings.AGENT_EXTRACTOR_LLM_MODEL,
                schema=schema,
            )
            metadata = agent_extract.extract_metadata(
                texts=texts,
                images=images,
            )

    return {"category": category, "metadata": metadata}
