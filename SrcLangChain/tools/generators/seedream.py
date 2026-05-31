from typing import Type, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...tools.generators.base import BaseGenerator
from ...services.llm_client import doubao_client
from ...config.settings import settings
from ...models.intent import IntentRepresentation


class SeedreamInput(BaseModel):
    prompt: str = Field(description="专业提示词", default="")
    intent_json: str = Field(description="JSON格式的IntentRepresentation（fallback）", default="")
    aspect_ratio: str = Field(description="画幅比例", default="1:1")


class SeedreamGenerator(BaseGenerator, BaseTool):
    """豆包 Seedream-5.0 图像生成 Tool"""

    name: str = "seedream_generator"
    description: str = (
        "调用豆包Seedream-5.0生成高质量图像。 "
        "输入：专业提示词（优先）或 JSON格式的IntentRepresentation（fallback）。 "
        "输出：生成图像的URL。"
    )
    args_schema: Type[BaseModel] = SeedreamInput

    @property
    def strengths(self) -> list:
        return ["photo_realistic", "high_detail", "chinese_prompt", "fast"]

    def translate(self, intent: IntentRepresentation) -> str:
        """
        原始提示词拼接逻辑（fallback 用）
        PromptEngineer 挂了的时候用这个
        """
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

    def generate(
        self,
        prompt: Optional[str] = None,
        intent: Optional[IntentRepresentation] = None,
        aspect_ratio: str = "1:1"
    ) -> str:
        """
        生成图像
        Args:
            prompt: PromptEngineer 设计好的专业提示词（优先）
            intent: IntentRepresentation（fallback，用内部 translate 拼接）
            aspect_ratio: 画幅比例
        """
        # 优先用 PromptEngineer 的提示词
        if prompt:
            final_prompt = prompt
            print(f"   📝 使用 PromptEngineer 提示词: {prompt[:100]}...")
        elif intent:
            final_prompt = self.translate(intent)
            print(f"   📝 使用 fallback 提示词: {final_prompt[:100]}...")
        else:
            raise ValueError("必须提供 prompt 或 intent")

        size = self.get_size(aspect_ratio)

        client = doubao_client
        model = settings.DOUBAO.model_id

        response = client.images.generate(
            model=model,
            prompt=final_prompt,
            size=size,
            response_format="url",
            extra_body={"watermark": False}
        )

        return response.data[0].url

    def _run(self, prompt: str = "", intent_json: str = "", aspect_ratio: str = "1:1") -> str:
        """LangChain Tool 接口"""
        if prompt:
            return self.generate(prompt=prompt, aspect_ratio=aspect_ratio)
        elif intent_json:
            intent = IntentRepresentation.from_dict(__import__('json').loads(intent_json))
            return self.generate(intent=intent, aspect_ratio=aspect_ratio)
        else:
            raise ValueError("必须提供 prompt 或 intent_json")

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError