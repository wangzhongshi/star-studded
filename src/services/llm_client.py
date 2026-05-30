import os
from openai import OpenAI
from typing import Optional, List, Dict, Any


class UnifiedLLMClient:
    """
    统一封装 DeepSeek / Qwen / Doubao 的 OpenAI 兼容调用
    """

    @staticmethod
    def deepseek_client() -> OpenAI:
        return OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    @staticmethod
    def qwen_client() -> OpenAI:
        return OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    @staticmethod
    def doubao_client() -> OpenAI:
        return OpenAI(
            api_key=os.getenv("ARK_API_KEY"),
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )


# 全局客户端实例
deepseek_client = UnifiedLLMClient.deepseek_client()
qwen_client = UnifiedLLMClient.qwen_client()
doubao_client = UnifiedLLMClient.doubao_client()