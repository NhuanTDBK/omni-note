from openai import AsyncClient
import tiktoken


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
