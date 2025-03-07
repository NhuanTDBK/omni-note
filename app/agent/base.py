from openai import Client


class BaseAgent(Client):
    def __init__(self, client: Client, model_id: str, prompt_template: str):
        self.client = client
        self.prompt_template = prompt_template
        self.model_id = model_id

    def set_system_prompt(self, sp: str):
        self.sp = sp
        return self