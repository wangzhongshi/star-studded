import json
from typing import Optional
from ..services.llm_client import deepseek_client
from ..config.settings import settings
from ..models.intent import IntentRepresentation, IntentMode, Subject, Style, Output, Constraints


class IntentParser:
    """
    DeepSeek 意图解析智能体
    """

    def __init__(self):
        self.client = deepseek_client
        self.model = settings.DEEPSEEK.model_id

    def parse(self, user_message: str, image_description: Optional[str] = None) -> IntentRepresentation:
        """
        调用 DeepSeek 解析用户意图
        """
        system_prompt = """你是一个专业的AI图像创作意图解析器。

请分析用户的自然语言描述，提取以下结构化信息：
1. 创作意图类型（style_transfer/element_swap/mood_shift/replicate/composite）
2. 主体描述（entity, attributes, pose, expression）
3. 风格偏好（genre, references, mood, intensity: 0-1）
4. 输出要求（format, aspect_ratio: 1:1/16:9/9:16/4:3, quality: high/medium/low）
5. 约束条件（must_include, avoid）

输出必须是严格的JSON格式，不要有任何其他文字。"""

        user_content = f"用户输入：{user_message}"
        if image_description:
            user_content = f"图像描述：{image_description}\n\n{user_content}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
            stream=False
        )

        intent_json = json.loads(response.choices[0].message.content)
        return self._json_to_intent(intent_json)

    def _json_to_intent(self, data: dict) -> IntentRepresentation:
        mode_map = {
            "style_transfer": IntentMode.STYLE_TRANSFER,
            "element_swap": IntentMode.ELEMENT_SWAP,
            "mood_shift": IntentMode.MOOD_SHIFT,
            "replicate": IntentMode.REPLICATE,
            "composite": IntentMode.COMPOSITE
        }

        return IntentRepresentation(
            mode=mode_map.get(data.get("mode", "style_transfer"), IntentMode.STYLE_TRANSFER),
            subject=Subject(
                entity=data.get("subject", {}).get("entity", ""),
                attributes=data.get("subject", {}).get("attributes", []),
                pose=data.get("subject", {}).get("pose", ""),
                expression=data.get("subject", {}).get("expression", "")
            ),
            style=Style(
                genre=data.get("style", {}).get("genre", ""),
                references=data.get("style", {}).get("references", []),
                mood=data.get("style", {}).get("mood", ""),
                intensity=data.get("style", {}).get("intensity", 0.5)
            ),
            output=Output(
                format=data.get("output", {}).get("format", "image"),
                aspect_ratio=data.get("output", {}).get("aspect_ratio", "1:1"),
                quality=data.get("output", {}).get("quality", "high")
            ),
            constraints=Constraints(
                must_include=data.get("constraints", {}).get("must_include", []),
                avoid=data.get("constraints", {}).get("avoid", [])
            )
        )