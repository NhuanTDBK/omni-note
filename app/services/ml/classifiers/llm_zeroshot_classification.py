import json
import base64
from PIL import Image
from typing import List

from openai import AsyncClient
from app.configs import Config
from app.services.ml.base import BaseAgent


class MultiModalClassificationAgent(BaseAgent):
    def __init__(self, client, model_id):
        prompt_template = """
            You are analyzing the content and classifying into one of these categories {}
            Be concise and truthful" \
        """
        super().__init__(
            client,
            model_id=model_id,
            prompt_template=prompt_template,
        )
        self.sp = "You are an helpful AI Visual Assistant"
        self.max_tokens = 8096

    @staticmethod
    def from_config(config: Config):
        client = AsyncClient(
            api_key=config.VISUAL_AGENT_CATEGORIZATION_LLM_API_KEY,
            base_url=config.VISUAL_AGENT_CATEGORIZATION_LLM_URL,
        )
        model_id = config.VISUAL_AGENT_CATEGORIZATION_LLM_MODEL
        return MultiModalClassificationAgent(client, model_id)

    async def classify_content(
        self,
        categories: List[str],
        texts: List[str] = [],
        images: List[Image.Image] = [],
        temperature: float = 0.6,
        **kwargs,
    ) -> str:

        content = []

        for image in images:
            encoded_image = base64.b64encode(image.tobytes())
            decoded_image_text = encoded_image.decode("utf-8")
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{decoded_image_text}"
                    },
                },
            )
        content.append(
            {
                "type": "text",
                "text": self.prompt_template.format(",".join(categories)),
            }
        )
        for text in texts:
            content.append(
                {
                    "type": "text",
                    "text": text,
                }
            )

        sp, response_format = self.get_structured_output(
            self.model_id,
            schema={
                "$defs": {
                    "CategoryEnum": {
                        "enum": categories,
                        "title": "CategoryEnum",
                        "type": "string",
                    }
                },
                "properties": {"c": {"$ref": "#/$defs/CategoryEnum"}},
                "required": ["c"],
                "title": "Category",
                "type": "object",
            },
        )            

        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": sp,
                    }
                ],
            },
            {"role": "user", "content": content},
        ]

        response = await self.client.beta.chat.completions.parse(
            messages=messages,
            model=self.model_id,
            max_tokens=self.max_tokens,
            temperature=temperature,
            response_format=response_format,
            **kwargs,
        )
        raw_response = response.choices[0].message.content
        response = json.loads(raw_response)

        return response["c"]


class TextClassificationAgent(BaseAgent):
    def __init__(self, client, model_id):
        prompt_template = """
            You are analyzing the content and classifying into one of these categories {categories}
            Be concise and truthful
            # Input
            {input} \
        """
        super().__init__(
            client,
            model_id=model_id,
            prompt_template=prompt_template,
        )
        self.sp = "You are an helpful AI Assistant"
        self.max_tokens = 8096

    @staticmethod
    def from_config(config: Config):
        client = AsyncClient(
            api_key=config.TEXT_AGENT_CATEGORIZATION_LLM_API_KEY,
            base_url=config.TEXT_AGENT_CATEGORIZATION_LLM_URL,
        )
        model_id = config.TEXT_AGENT_CATEGORIZATION_LLM_MODEL
        return TextClassificationAgent(client, model_id)

    async def classify_content(
        self,
        categories: List[str],
        texts: List[str] = [],
        temperature: float = 0.6,
        **kwargs,
    ) -> str:

        content = self.prompt_template.format(
            categories=",".join(categories), input=",".join(texts)
        )

        sp, response_format = self.get_structured_output(
            self.model_id,
            schema={
                "$defs": {
                    "CategoryEnum": {
                        "enum": categories,
                        "title": "CategoryEnum",
                        "type": "string",
                    }
                },
                "properties": {"c": {"$ref": "#/$defs/CategoryEnum"}},
                "required": ["c"],
                "title": "Category",
                "type": "object",
            },
        )
        messages = [
            {
                "role": "system",
                "content": sp,
            },
            {"role": "user", "content": content},
        ]

        response = await self.client.beta.chat.completions.parse(
            messages=messages,
            model=self.model_id,
            max_tokens=self.max_tokens,
            temperature=temperature,
            response_format=response_format,
            **kwargs,
        )
        raw_response = response.choices[0].message.content
        response = json.loads(raw_response)

        return response["c"]
