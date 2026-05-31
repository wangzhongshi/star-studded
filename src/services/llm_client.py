# Copyright 2026 王柄屹
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from openai import OpenAI
from typing import Optional


class LLMClient:
    """统一 LLM 客户端工厂"""

    _clients = {}

    @classmethod
    def get_deepseek(cls) -> Optional[OpenAI]:
        if "deepseek" not in cls._clients:
            from ..config.settings import get_settings
            settings = get_settings()
            api_key = settings.DEEPSEEK.api_key
            if not api_key:
                return None
            cls._clients["deepseek"] = OpenAI(
                api_key=api_key,
                base_url=settings.DEEPSEEK.base_url
            )
        return cls._clients["deepseek"]

    @classmethod
    def get_qwen(cls) -> Optional[OpenAI]:
        if "qwen" not in cls._clients:
            from ..config.settings import get_settings
            settings = get_settings()
            api_key = settings.QWEN.api_key
            if not api_key:
                return None
            cls._clients["qwen"] = OpenAI(
                api_key=api_key,
                base_url=settings.QWEN.base_url
            )
        return cls._clients["qwen"]

    @classmethod
    def get_doubao(cls) -> Optional[OpenAI]:
        if "doubao" not in cls._clients:
            from ..config.settings import get_settings
            settings = get_settings()
            api_key = settings.DOUBAO.api_key
            if not api_key:
                return None
            cls._clients["doubao"] = OpenAI(
                api_key=api_key,
                base_url=settings.DOUBAO.base_url
            )
        return cls._clients["doubao"]


# 模块级别初始化：允许失败，返回 None
def _init_client(name, getter):
    try:
        client = getter()
        if client is None:
            print(f"⚠️  {name} API Key 未设置，客户端未初始化")
        return client
    except Exception as e:
        print(f"⚠️  {name} 初始化失败: {e}")
        return None

deepseek_client = _init_client("DeepSeek", LLMClient.get_deepseek)
qwen_client = _init_client("Qwen", LLMClient.get_qwen)
doubao_client = _init_client("Doubao", LLMClient.get_doubao)