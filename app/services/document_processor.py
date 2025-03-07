from typing import BinaryIO
import magic
import os
from app.config import get_settings

settings = get_settings()

class DocumentProcessor:
    @staticmethod
    def detect_mime_type(file: BinaryIO) -> str:
        """Detect the MIME type of the uploaded file"""
        mime = magic.Magic(mime=True)
        file_content = file.read(2048)  # Read first 2KB for MIME detection
        file.seek(0)  # Reset file pointer
        return mime.from_buffer(file_content)
    
    @staticmethod
    async def process_document(file: BinaryIO, filename: str) -> dict:
        """Process an uploaded document and extract relevant information"""
        mime_type = DocumentProcessor.detect_mime_type(file)
        
        # Save file
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(file.read())
        
        return {
            "mime_type": mime_type,
            "file_path": file_path,
            # More metadata to be added
        }
