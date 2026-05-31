import os
from openai import OpenAI
from typing import Optional


class LLMClient:
    """统一 LLM 客户端工厂"""

    _clients = {}

    @classmethod
    def get_deepseek(cls) -> OpenAI:
        if "deepseek" not in cls._clients:
            from ..config.settings import settings
            cls._clients["deepseek"] = OpenAI(
                api_key=settings.DEEPSEEK.api_key,
                base_url=settings.DEEPSEEK.base_url
            )
        return cls._clients["deepseek"]

    @classmethod
    def get_qwen(cls) -> OpenAI:
        if "qwen" not in cls._clients:
            from ..config.settings import settings
            cls._clients["qwen"] = OpenAI(
                api_key=settings.QWEN.api_key,
                base_url=settings.QWEN.base_url
            )
        return cls._clients["qwen"]

    @classmethod
    def get_doubao(cls) -> OpenAI:
        if "doubao" not in cls._clients:
            from ..config.settings import settings
            cls._clients["doubao"] = OpenAI(
                api_key=settings.DOUBAO.api_key,
                base_url=settings.DOUBAO.base_url
            )
        return cls._clients["doubao"]


# 便捷导入
deepseek_client = LLMClient.get_deepseek()
qwen_client = LLMClient.get_qwen()
doubao_client = LLMClient.get_doubao()