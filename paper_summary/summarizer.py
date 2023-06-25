from paper_summary import env
import openai
import tiktoken
import re

MAX_SIZE = 16_000


class Summarizer:
    def __init__(self, text=str, model_name: str = env.DEFAULET_MODEL) -> None:
        self.model_name = model_name
        self.text = self.sanitize_text(text)
        self.encoder = tiktoken.encoding_for_model(model_name)

    @property
    def tokens_count(self) -> int:
        tokens = self.encoder.encode(self.text, disallowed_special="all")
        return len(tokens)

    def sanitize_text(self, text: str) -> str:
        return re.sub(r"<\|\w+\|>", "", text)

    def get_key_points(self) -> str:
        prompt = (
            "Summarize the following text and give me "
            + "(1) Why is this important, (2) How did they achieve this?,"
            + " (3) What is the novelty of this, (4) What are the key findings."
            + "\nProvide a few bullet points for each."
            + "\n\n"
            + self.text
        )

        return self._call_chat_api(prompt)

    def get_summary(self) -> str:
        prompt = f"Summarize the following text into four paragraphs:\n\n{self.text}"
        return self._call_chat_api(prompt)

    def _call_chat_api(self, prompt) -> str:
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return response["choices"][0]["message"]["content"]

    def check_length(self) -> None:
        n_tokens = self.tokens_count
        if n_tokens > MAX_SIZE:
            raise ValueError(f"Text length {n_tokens} exceeds maximum allowed length {MAX_SIZE}")
