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
import json
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ..services.llm_client import deepseek_client
from ..config.settings import settings
from ..models.intent import IntentRepresentation


class IntentParserInput(BaseModel):
    user_message: str = Field(description="用户的自然语言描述")
    image_description: Optional[str] = Field(default=None, description="图像描述（如果有上传图片）")


class IntentParserTool(BaseTool):
    """DeepSeek 意图解析 Tool"""

    name: str = "intent_parser"
    description: str = (
        "解析用户的创作意图，将自然语言转换为结构化的JSON格式。 "
        "输入：用户描述 + 可选的图像描述。 "
        "输出：JSON格式的IntentRepresentation，包含mode/subject/style/output/constraints。"
    )
    args_schema: Type[BaseModel] = IntentParserInput

    def _run(self, user_message: str, image_description: Optional[str] = None) -> str:
        client = deepseek_client
        model = settings.DEEPSEEK.model_id

        system_prompt = """你是一个专业的AI图像创作意图解析器。

请分析用户的自然语言描述，提取以下结构化信息并输出JSON：

{
    "mode": "style_transfer|element_swap|mood_shift|replicate|composite",
    "subject": {
        "entity": "主体名称",
        "attributes": ["特征1", "特征2"],
        "pose": "姿态",
        "expression": "表情"
    },
    "style": {
        "genre": "风格流派",
        "references": ["参考作品/艺术家"],
        "mood": "情绪氛围",
        "intensity": 0.8
    },
    "output": {
        "format": "image",
        "aspect_ratio": "1:1|16:9|9:16|4:3",
        "quality": "high|medium|low"
    },
    "constraints": {
        "must_include": ["必须包含的元素"],
        "avoid": ["需要避免的元素"]
    }
}

规则：
- 如果用户上传了图片，参考图像描述来理解主体
- mode默认style_transfer，如果用户说"换成xxx风格"
- intensity根据情绪词判断：很酷=0.9，稍微=0.3
- attributes必须是列表，没有就填[]
- 只输出JSON，不要任何其他文字"""

        user_content = f"用户输入：{user_message}"
        if image_description:
            user_content = f"图像描述：{image_description}\n\n{user_content}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
            stream=False
        )

        intent_json = response.choices[0].message.content
        return intent_json

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("异步模式暂不支持")