# processors/file_type_detector.py
import os
import magic
from app.logger import logger


def detect_file_type(file):
    """
    Detect the type of uploaded file

    Args:
        file: The uploaded file object

    Returns:
        str: File type identifier (pdf, image, text, voice_memo, web_link)
    """
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)  # Reset file pointer

    # Map mime types to our application types
    if mime_type.startswith("application/pdf"):
        return "pdf"
    elif mime_type.startswith("image/"):
        return "image"
    elif mime_type.startswith("audio/"):
        return "voice_memo"
    elif mime_type.startswith("text/"):
        return "text"
    # Additional type detection logic...

    logger.info(f"Detected file type: {mime_type}")
    return None
