from typing import Dict, Any
from ..models.intent import IntentRepresentation
from ..tools.generators.seedream import SeedreamGenerator


class GeneratorAgent:
    """
    生成智能体
    职责：调用具体模型生成图像
    """

    def __init__(self):
        self.generators = {
            "seedream": SeedreamGenerator()
        }

    def generate(self, prompt: str, model: str, aspect_ratio: str = "1:1") -> str:
        """
        调用选定模型生成
        Args:
            prompt: PromptEngineer 设计好的专业提示词
            model: 模型标识
            aspect_ratio: 画幅比例
        """
        generator = self.generators.get(model)
        if not generator:
            raise ValueError(f"未知模型: {model}")

        return generator.generate(prompt=prompt, aspect_ratio=aspect_ratio)