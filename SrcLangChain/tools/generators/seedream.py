from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...tools.generators.base import BaseGenerator
from ...services.llm_client import doubao_client
from ...config.settings import settings
from ...models.intent import IntentRepresentation


class SeedreamInput(BaseModel):
    intent_json: str = Field(description="JSON格式的IntentRepresentation")


class SeedreamGenerator(BaseGenerator, BaseTool):
    """豆包 Seedream-5.0 图像生成 Tool"""

    name: str = "seedream_generator"
    description: str = (
        "调用豆包Seedream-5.0生成高质量图像。 "
        "输入：JSON格式的IntentRepresentation。 "
        "输出：生成图像的URL。"
    )
    args_schema: Type[BaseModel] = SeedreamInput

    @property
    def strengths(self) -> list:
        return ["photo_realistic", "high_detail", "chinese_prompt", "fast"]

    def translate(self, intent: IntentRepresentation) -> str:
        parts = []

        # 主体
        subject_desc = intent.subject.entity
        if intent.subject.attributes:
            subject_desc += f"，{', '.join(intent.subject.attributes)}"
        if intent.subject.pose:
            subject_desc += f"，{intent.subject.pose}"
        if intent.subject.expression:
            subject_desc += f"，表情{intent.subject.expression}"
        if subject_desc:
            parts.append(subject_desc)

        # 风格
        if intent.style.genre:
            parts.append(f"{intent.style.genre}风格")
        if intent.style.references:
            parts.append(f"参考{', '.join(intent.style.references)}")

        # 情绪
        if intent.style.mood:
            parts.append(f"{intent.style.mood}氛围")

        # 质量词
        if intent.output.quality == "high":
            parts.extend([
                "超精细", "8K", "电影级", "光线追踪",
                "极致光影", "质感真实", "视觉冲击"
            ])

        # 约束
        if intent.constraints.must_include:
            parts.append(f"包含：{', '.join(intent.constraints.must_include)}")

        return "，".join(parts) if parts else "高质量图像"

    def get_size(self, aspect_ratio: str) -> str:
        """Seedream 最小要求 3686400 像素"""
        ratio_map = {
            "1:1": "1920x1920",
            "16:9": "2560x1440",
            "9:16": "1440x2560",
            "4:3": "2560x1920",
            "3:4": "1920x2560",
        }
        return ratio_map.get(aspect_ratio, "1920x1920")

    def generate(self, intent: IntentRepresentation) -> str:
        prompt = self.translate(intent)
        size = self.get_size(intent.output.aspect_ratio)

        client = doubao_client
        model = settings.DOUBAO.model_id

        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            response_format="url",
            extra_body={"watermark": False}
        )

        return response.data[0].url

    def _run(self, intent_json: str) -> str:
        """LangChain Tool 接口"""
        intent = IntentRepresentation.from_dict(__import__('json').loads(intent_json))
        return self.generate(intent)

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError