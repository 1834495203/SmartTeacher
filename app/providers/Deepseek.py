import os
from typing import Any, Dict, Optional, List

import yaml
from openai import OpenAI

from providers.ProvidersBase import AbstractChat


class DeepSeekChat(AbstractChat):
    def __init__(self, model: str, api_key: Optional[str] = None):
        if api_key is None:
            BASE_DIR = os.path.dirname(__file__)  # 获取 当前文件 所在目录
            with open(f"{BASE_DIR}\\config\\api.yml") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                api_key = config['resource']['deepseek']['api']
        
        super().__init__(model)
        
        if model not in ["deepseek-reasoner", "deepseek-chat"]:
            raise ValueError("模型必须是 'deepseek-reasoner' 或 'deepseek-chat'")
        
        # 初始化客户端
        self.client = self._create_client(api_key)

    def call_api(self, messages: List[Dict[str, str]], stream: bool) -> Any:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
        )

    def _create_client(self, api_key: str, **kwargs) -> OpenAI:
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        return {
            "content": response.choices[0].message.content,
            "reasoning_content": getattr(response.choices[0].message, "reasoning_content", None),
            "finish_reason": response.choices[0].finish_reason,
            "message": response
        }

    def parse_chunk(self, chunk: Any) -> Dict[str, Any]:
        return {
            "content": chunk.choices[0].delta.content,
            "reasoning_content": getattr(chunk.choices[0].delta, "reasoning_content", None)
        }
