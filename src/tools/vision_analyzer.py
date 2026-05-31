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
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ..services.llm_client import qwen_client
from ..config.settings import settings


class VisionAnalyzerInput(BaseModel):
    image_path: str = Field(description="本地图片文件的绝对路径")
    task: str = Field(default="describe", description="任务类型：describe(描述) 或 reverse_prompt(反推提示词)")


class VisionAnalyzerTool(BaseTool):
    """Qwen 视觉分析 Tool"""

    name: str = "vision_analyzer"
    description: str = (
        "分析图片内容。支持两个任务："
        "1. describe - 详细描述图片的主体、场景、风格、光影、色彩、情绪；"
        "2. reverse_prompt - 反推适合AI生成的提示词（英文关键词格式）。"
        "输入：本地图片路径 + 任务类型。"
    )
    args_schema: Type[BaseModel] = VisionAnalyzerInput

    def _run(self, image_path: str, task: str = "describe") -> str:
        client = qwen_client
        model = settings.QWEN.model_id

        # 读取图片
        image_base64 = self._image_to_base64(image_path)

        if task == "describe":
            text_prompt = "请详细描述这张图片的内容，包括：主体、场景、风格、光影、色彩、情绪氛围。用中文回答，300字以内。"
        elif task == "reverse_prompt":
            text_prompt = "请反推这张图片的AI生成提示词。输出格式：英文逗号分隔的关键词列表，适合Stable Diffusion/Flux模型。包含：主体、风格、光影、构图、质量词。"
        else:
            return f"未知任务类型: {task}"

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
                        "text": text_prompt
                    }
                ]
            }
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"enable_thinking": True},
            stream=False
        )

        return response.choices[0].message.content

    def _image_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("异步模式暂不支持")