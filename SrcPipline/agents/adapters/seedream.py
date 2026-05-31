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
from ...services.llm_client import doubao_client
from ...config.settings import settings
from ...models.intent import IntentRepresentation


class SeedreamAdapter:
    """
    Doubao-Seedream-5.0 适配器
    """

    def __init__(self):
        self.client = doubao_client
        self.model = settings.DOUBAO.model_id

    def translate(self, intent: IntentRepresentation) -> str:
        """
        将意图表示翻译为 Seedream 提示词
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
        elif intent.output.quality == "medium":
            parts.append("中等质量")

        # 约束
        if intent.constraints.must_include:
            parts.append(f"包含：{', '.join(intent.constraints.must_include)}")

        return "，".join(parts)

    def get_size(self, aspect_ratio: str) -> str:
        """
        Seedream 最小要求 3686400 像素 (~1920x1920)
        """
        ratio_map = {
            "1:1": "1920x1920",  # 3,686,400 ✓
            "16:9": "2560x1440",  # 3,686,400 ✓
            "9:16": "1440x2560",  # 3,686,400 ✓
            "4:3": "2560x1920",  # 4,915,200 ✓
            "3:4": "1920x2560",  # 4,915,200 ✓
            "2:3": "1920x2880",  # 5,529,600 ✓
        }
        return ratio_map.get(aspect_ratio, "1920x1920")

    def generate(self, intent: IntentRepresentation) -> str:
        """
        调用 Seedream API 生成图像
        """
        prompt = self.translate(intent)
        size = self.get_size(intent.output.aspect_ratio)

        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            response_format="url",
            extra_body={"watermark": False}
        )

        return response.data[0].url