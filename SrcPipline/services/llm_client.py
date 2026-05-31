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