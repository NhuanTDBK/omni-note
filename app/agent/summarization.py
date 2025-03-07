from app.agent.base import BaseAgent


en_en_tone = """Use British English and exclusively British (UK) English.
Strictly follow UK spelling conventions (e.g., use 'colour' not 'color', 'realise' not 'realize').
Use UK vocabulary and phrases (e.g., 'flat' not 'apartment', 'lorry' not 'truck').
Apply UK formatting standards.
Do not use American English spellings, terms, or formats under any circumstances
"""
en_us_tone = """Use American English and exclusively American (US) English.
Strictly follow US spelling conventions (e.g., use 'color' not 'colour', 'realize' not 'realise').
Use US vocabulary and phrases (e.g., 'apartment' not 'flat', 'truck' not 'lorry').
Apply US formatting standards.
Do not use British English spellings, terms, or formats under any circumstances
"""
vi_tone = """Use Vietnamese language and exclusively Vietnamese.
Strictly follow Vietnamese spelling conventions.
Use Vietnamese vocabulary and phrases.
Apply Vietnamese formatting standards.
"""

TONE_MAPPING = {
    "en_us": en_us_tone,
    "en_en": en_en_tone,
    "vi": vi_tone,
}


class ContentSummarizer(BaseAgent):
    def __init__(self, client, model_id, lang: str = "en_us"):
        tone_template = TONE_MAPPING.get(lang, en_us_tone)
        prompt_template = """
        ### Instruction: Write a concise summary. Return in string only.
        ### Guideline:
        Please adhere to the following guidelines:
        - The summary should be in English, easily understood at a high-school education level.
        - Keep the summary concise and informative, at most 5 sentences.
        - Only provide a summary, no self-explanatory content
        - {tone_template}

        ### Input
        {{content}}

        ### Response
        """.format(
            tone_template=tone_template
        )
        super().__init__(client, model_id, prompt_template)
        self.lang = lang
        self.max_tokens = 4096
        self.max_input_tokens = 8096
        self.sp = "You are an helpful AI Content Summarizer for user taking notes"

    async def summarize_content(
        self,
        content: str,
    ) -> str:
        prompt = self.prompt_template.format(content=content)
        prompt = self.truncate_text(prompt)
        response = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self.sp,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.6,
            max_completion_tokens=self.max_tokens,
            model=self.model_id,
        )
        return response.choices[0].message.content
