# Grok 类
import os
from typing import Optional

import yaml
from openai import OpenAI

from providers.Openai import OpenAIChat


class GrokChat(OpenAIChat):
    def __init__(self, model, api_key: Optional[str] = None):
        if api_key is None:
            BASE_DIR = os.path.dirname(__file__)  # 获取 当前文件 所在目录
            with open(f"{BASE_DIR}\config\\api.yml") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                api_key = config['resource']['grok']['api']
        super().__init__(api_key, model)
        if model not in ["grok-3-mini", "grok-3", "grok-2-image"]:
            raise ValueError("模型必须是 grok-3-mini, grok-3, grok-2-image")

    def _create_client(self, api_key: str, **kwargs) -> OpenAI:
        return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")


