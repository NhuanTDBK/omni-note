from openai import AsyncClient
import json
import tiktoken

STRUCTURED_OUTPUT_PROVIDERS = ["openai", "localhost"]


class BaseAgent(AsyncClient):
    def __init__(self, client: AsyncClient, model_id: str, prompt_template: str):
        self.client = client
        self.prompt_template = prompt_template
        self.model_id = model_id
        self.max_input_tokens = 4096
        self.model_encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def truncate_text(self, text: str):
        encoded_tokens = self.model_encoding.encode(text)[: self.max_input_tokens]
        return self.model_encoding.decode(encoded_tokens)

    def set_system_prompt(self, sp: str):
        self.sp = sp
        return self

    def get_structured_output(self, model_id: str, schema: dict):
        system_prompt = self.sp
        is_support_structured_output = any(
            [
                provider in self.client.base_url.host
                for provider in STRUCTURED_OUTPUT_PROVIDERS
            ]
        )
        if is_support_structured_output:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": schema,
                },
            }
        else:
            response_format = {"type": "json_object"}
            system_prompt += (
                "\n. Return in JSON format structure as below:\n"
                + json.dumps(schema, indent=4)
            )

        return system_prompt, response_format
