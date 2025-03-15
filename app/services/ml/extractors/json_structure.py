from typing import List, Dict, Any
import base64
import json
from io import BytesIO
from pydantic import BaseModel
from openai import AsyncClient
from app.services.ml.base import BaseAgent
from app.configs import Config


class MultiModalJsonStructureExtractor(BaseAgent):
    """
    A class for extracting structured metadata from text and images using an AI model.
    This class extends BaseAgent and provides functionality to extract structured data
    from a combination of text inputs and images according to a specified schema.
    Parameters
    ----------
    client : object
        The AI model client instance used for making API calls
    model_id : str
        The identifier for the AI model to be used
    schema : Union[Dict[str, Any], BaseModel]
        The schema defining the structure of the extracted data. Can be either a dictionary
        or a Pydantic model.
    Attributes
    ----------
    max_tokens : int
        Maximum number of tokens for the model response (default: 1024)
    sp : str
        System prompt for the AI model
    response_format : dict
        Format specification for the model response based on the provided schema
    Methods
    -------
    extract_metadata(texts: List[str], images_path: List[str] = None, temperature: float = 0.6, **kwargs)
        Extracts structured metadata from the provided texts and images.
        Parameters:
            texts (List[str]): List of text inputs to process
            images_path (List[str], optional): List of paths to image files
            temperature (float, optional): Temperature parameter for model response (default: 0.6)
            **kwargs: Additional arguments to pass to the model
        Returns:
            The structured metadata extracted according to the specified schema
    Raises
    ------
    ValueError
        If the schema parameter is neither a dictionary nor a Pydantic model
    """

    def __init__(self, client, model_id: str):
        prompt_template = """
        # Instruction
        Extract structured data from the provided text
        # Guideline
        - Be concise and truthful
        - Auto correct the text if needed
        """
        super().__init__(client, model_id, prompt_template)
        self.max_tokens = 1024
        self.sp = "You are an helpful AI OCR Assistant"

    @staticmethod
    def from_config(config: Config):
        client = AsyncClient(
            api_key=config.VISUAL_AGENT_EXTRACTOR_LLM_API_KEY,
            base_url=config.VISUAL_AGENT_EXTRACTOR_LLM_URL,
        )
        model_id = config.VISUAL_AGENT_EXTRACTOR_LLM_MODEL
        return MultiModalJsonStructureExtractor(client, model_id)

    async def extract_metadata(
        self,
        schema: Dict[str, Any],
        texts: List[str],
        images: List[str] = [],
        temperature: float = 0.6,
        **kwargs,
    ):
        if isinstance(schema, dict):
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": schema,
                },
            }
        elif isinstance(schema, BaseModel):
            response_format = schema
        else:
            raise ValueError("Schema must be a dict or a Pydantic model")
        content = []
        for text in texts:
            content.append(
                {
                    "type": "text",
                    "text": text,
                }
            )
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
                "text": self.prompt_template,
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
        response = await self.client.beta.chat.completions.parse(
            messages=messages,
            model=self.model_id,
            max_tokens=self.max_tokens,
            temperature=temperature,
            response_format=response_format,
            **kwargs,
        )
        return json.loads(response.choices[0].message.content)


class OCRJsonStructureExtractor(BaseAgent):
    """
    A class for extracting structured metadata from text and images using an AI model.
    This class extends BaseAgent and provides functionality to extract structured data
    from a combination of text inputs and images according to a specified schema.
    Parameters
    ----------
    client : object
        The AI model client instance used for making API calls
    model_id : str
        The identifier for the AI model to be used
    schema : Union[Dict[str, Any], BaseModel]
        The schema defining the structure of the extracted data. Can be either a dictionary
        or a Pydantic model.
    Attributes
    ----------
    max_tokens : int
        Maximum number of tokens for the model response (default: 1024)
    sp : str
        System prompt for the AI model
    response_format : dict
        Format specification for the model response based on the provided schema
    Methods
    -------
    extract_metadata(texts: List[str], images_path: List[str] = None, temperature: float = 0.6, **kwargs)
        Extracts structured metadata from the provided texts and images.
        Parameters:
            texts (List[str]): List of text inputs to process
            images_path (List[str], optional): List of paths to image files
            temperature (float, optional): Temperature parameter for model response (default: 0.6)
            **kwargs: Additional arguments to pass to the model
        Returns:
            The structured metadata extracted according to the specified schema
    Raises
    ------
    ValueError
        If the schema parameter is neither a dictionary nor a Pydantic model
    """

    def __init__(self, client, model_id: str):
        prompt_template = """
        # Instruction
        Extract structured data from the provided text
        # Guideline
        - Be concise and truthful
        - Auto correct the text if needed
        """
        super().__init__(client, model_id, prompt_template)
        self.max_tokens = 1024
        self.sp = "You are an helpful AI OCR Assistant"

    @staticmethod
    def from_config(config: Config):
        client = AsyncClient(
            api_key=config.VISUAL_AGENT_EXTRACTOR_LLM_API_KEY,
            base_url=config.VISUAL_AGENT_EXTRACTOR_LLM_URL,
        )
        model_id = config.VISUAL_AGENT_EXTRACTOR_LLM_MODEL
        return OCRJsonStructureExtractor(client, model_id)

    async def extract_metadata(
        self,
        schema: Dict[str, Any],
        texts: List[str],
        temperature: float = 0.6,
        **kwargs,
    ):
        if isinstance(schema, dict):
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": schema,
                },
            }
        elif isinstance(schema, BaseModel):
            response_format = schema
        else:
            raise ValueError("Schema must be a dict or a Pydantic model")
        content = []
        for text in texts:
            content.append(
                {
                    "content": text,
                }
            )
        content.append(
            {
                "content": self.prompt_template,
            }
        )

        messages = [
            {
                "role": "system",
                "content": self.sp,
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
        return json.loads(response.choices[0].message.content)
