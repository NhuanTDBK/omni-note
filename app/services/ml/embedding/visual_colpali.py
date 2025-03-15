from typing import List
from PIL import Image

import torch
from transformers.utils.import_utils import is_flash_attn_2_available
from colpali_engine.models import ColQwen2, ColQwen2Processor


class VisualModelEmbedding:
    def __init__(self, model_id: str, device: str = None, torch_dtype: str = None):
        if not device:
            device = "cpu"
            if torch.cuda.is_available():
                device = "cuda"
            if torch.mps.is_available():
                device = "mps"

        torch_dtype = torch.float16 if not torch_dtype else torch_dtype
        if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
            torch_dtype = torch.bfloat16

        self.model = ColQwen2.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            device_map=device,  # or "mps" if on Apple Silicon
            attn_implementation=(
                "flash_attention_2" if is_flash_attn_2_available() else None
            ),
        ).eval()

        self.processor = ColQwen2Processor.from_pretrained(model_id)

    def get_image_embedding(self, images: List[Image.Image]):
        batch_images = self.processor.process_images(images).to(self.device)
        with torch.no_grad():
            image_embeddings = self.model(**batch_images).detach().cpu().numpy()
            return image_embeddings

    def get_text_embedding(self, queries: List[str]):
        batch_queries = self.processor.process_queries(queries).to(self.device)
        with torch.no_grad():
            query_embeddings = self.model(**batch_queries).detach().cpu().numpy()
            return query_embeddings
