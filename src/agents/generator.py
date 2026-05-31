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