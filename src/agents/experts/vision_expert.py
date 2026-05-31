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
from typing import Dict, Any
from ...services.llm_client import qwen_client
from ...config.settings import settings


class VisionExpert:
    """
    视觉专家 - Qwen-VL
    职责：分析图像内容，提取视觉信息
    """

    def __init__(self):
        self.client = qwen_client
        self.model = settings.QWEN.model_id

    def analyze(self, image_path: str) -> Dict[str, str]:
        """
        分析图片，返回结构化视觉信息
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
                        "text": "请分析这张图片，输出以下信息（JSON格式）：\n"
                                "{\n"
                                "  \"subject\": \"主体描述\",\n"
                                "  \"scene\": \"场景描述\",\n"
                                "  \"style\": \"风格特征\",\n"
                                "  \"lighting\": \"光影特点\",\n"
                                "  \"color\": \"色彩特征\",\n"
                                "  \"mood\": \"情绪氛围\"\n"
                                "}"
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

        import json
        content = response.choices[0].message.content

        # 尝试提取JSON
        try:
            # 如果模型直接返回JSON
            result = json.loads(content)
        except json.JSONDecodeError:
            # 如果模型返回了额外文字，提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {"raw_description": content}

        return {
            "expert": "vision",
            "output": result
        }

    def _image_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")