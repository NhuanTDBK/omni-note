import json
import base64
from io import BytesIO
from typing import List, BinaryIO

from app.agent.base import BaseAgent


class ClassificationAgent(BaseAgent):
    def __init__(self, client, categories: List[str], model_id):
        self.prompt_template = "classify image into one of these categories {}"
        super().__init__(
            client,
            model_id=model_id,
            prompt_template=self.prompt_template,
        )
        self.categories = categories
        self.sp = "You are an helpful AI Visual Assistant"
        self.max_tokens = max([len(category) for category in self.categories]) + 32

    def classify_content(
        self,
        texts: List[str] = [],
        images: List[BytesIO] = [],
        temperature: float = 0.6,
        **kwargs,
    ):

        content = []

        for image in images:
            encoded_image = base64.b64encode(BytesIO(image).read())
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
                "text": self.prompt_template.format(",".join(self.categories)),
            }
        )
        for text in texts:
            content.append(
                {
                    "type": "text",
                    "text": text,
                }
            )

        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.sp,
                    }
                ],
            },
            {"role": "user", "content": content},
        ]

        response = self.client.beta.chat.completions.parse(
            messages=messages,
            model=self.model_id,
            max_tokens=self.max_tokens,
            temperature=temperature,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "category_response",
                    "schema": {
                        "$defs": {
                            "CategoryEnum": {
                                "enum": self.categories,
                                "title": "CategoryEnum",
                                "type": "string",
                            }
                        },
                        "properties": {"c": {"$ref": "#/$defs/CategoryEnum"}},
                        "required": ["c"],
                        "title": "Category",
                        "type": "object",
                    },
                },
            },
            **kwargs,
        )
        raw_response = response.choices[0].message.content
        response = json.loads(raw_response)

        return response["c"]
