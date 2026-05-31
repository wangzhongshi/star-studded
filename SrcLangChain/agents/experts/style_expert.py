import json
from typing import Dict, Any
from ...services.llm_client import deepseek_client
from ...config.settings import settings


class StyleExpert:
    """
    风格专家 - DeepSeek
    职责：识别艺术风格、流派、参考艺术家
    """

    def __init__(self):
        self.client = deepseek_client
        self.model = settings.DEEPSEEK.model_id

    def analyze(self, user_input: str, image_description: str = "") -> Dict[str, Any]:
        """
        分析风格需求
        """
        system_prompt = """你是一个风格识别专家。分析用户的风格需求，输出JSON格式：

{
    "genre": "主要流派（如赛博朋克、印象派、二次元）",
    "references": ["参考艺术家或作品"],
    "techniques": ["技法特征"],
    "era": "时代特征",
    "confidence": 0.9
}

重要：你的输出必须是JSON格式。"""  # 包含 "JSON" 字样

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
            "expert": "style",
            "output": result
        }