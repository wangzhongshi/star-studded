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
import base64
from typing import Optional
from ..services.llm_client import qwen_client
from ..config.settings import settings


class VisionAnalyzer:
    """
    Qwen3.6 视觉理解智能体
    """

    def __init__(self):
        self.client = qwen_client
        self.model = settings.QWEN.model_id

    def describe(self, image_path: str) -> str:
        """
        调用 Qwen3.6 描述图像内容
        """
        image_base64 = self._image_to_base64(image_path)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "请详细描述这张图片的内容，包括：主体、场景、风格、光影、色彩、情绪氛围。用中文回答，300字以内。"
                    }
                ]
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            extra_body={"enable_thinking": True},
            stream=False
        )

        return response.choices[0].message.content

    def reverse_prompt(self, image_path: str) -> str:
        """
        反推图片提示词（用于扩散模型）
        """
        image_base64 = self._image_to_base64(image_path)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "请反推这张图片的AI生成提示词。输出格式：主体描述+风格+光影+构图+质量词。用英文逗号分隔的关键词列表格式，适合Stable Diffusion/Flux模型。"
                    }
                ]
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )

        return response.choices[0].message.content

    @staticmethod
    def _image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")