import json
from typing import Dict, Any
from ...services.llm_client import deepseek_client
from ...config.settings import settings


class MoodExpert:
    """
    情绪专家 - DeepSeek
    职责：分析情绪、氛围、叙事
    """

    def __init__(self):
        self.client = deepseek_client
        self.model = settings.DEEPSEEK.model_id

    def analyze(self, user_input: str, image_description: str = "") -> Dict[str, Any]:
        """
        分析情绪需求
        """
        system_prompt = """你是一个情绪分析专家。分析用户的情绪需求，输出：

{
    "primary_mood": "主要情绪",
    "secondary_moods": ["次要情绪"],
    "intensity": 0.8,
    "narrative": "叙事感描述",
    "atmosphere": "氛围关键词"
}
重要：你的输出必须是JSON格式。"""

        content = f"用户输入: {user_input}"
        if image_description:
            content += f"\n图像描述: {image_description}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return {
            "expert": "mood",
            "output": result
        }