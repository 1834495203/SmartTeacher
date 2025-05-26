# OpenAIChat 类（不变）
from typing import List, Dict, Any

from openai import OpenAI

from providers.ProvidersBase import AbstractChat


class OpenAIChat(AbstractChat):
    def __init__(self, api_key: str, model: str):
        super().__init__(model)
        self.client = self._create_client(api_key)

    def _create_client(self, api_key: str, **kwargs) -> OpenAI:
        return OpenAI(api_key=api_key)

    def call_api(self, messages: List[Dict[str, str]], stream: bool) -> Any:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
        )

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        return {
            "content": response.choices[0].message.content,
            "finish_reason": response.choices[0].finish_reason,
            "message": response.choices[0].message
        }

    def parse_chunk(self, chunk: Any) -> Dict[str, Any]:
        return {
            "content": chunk.choices[0].delta.content,
        }
