import json
from typing import Dict, List, Any
from ..services.llm_client import deepseek_client
from ..config.settings import settings
from ..models.intent import IntentRepresentation


class FusionAgent:
    """
    融合智能体
    职责：整合多个专家输出，解决冲突，生成统一的 IntentRepresentation
    """

    def __init__(self):
        self.client = deepseek_client
        self.model = settings.DEEPSEEK.model_id

    def fuse(self, user_input: str, expert_outputs: List[Dict[str, Any]]) -> IntentRepresentation:
        """
        融合专家输出
        """
        # 构建专家输出摘要
        expert_summary = []
        for output in expert_outputs:
            expert_name = output.get("expert", "unknown")
            expert_data = output.get("output", {})
            expert_summary.append(f"【{expert_name}】{json.dumps(expert_data, ensure_ascii=False)}")

        system_prompt = """你是一个融合专家。你的任务是整合多个专家的输出，解决冲突，生成统一的创作意图。

输出必须是以下JSON格式：
{
    "mode": "style_transfer|element_swap|mood_shift|replicate|composite",
    "subject": {
        "entity": "主体",
        "attributes": ["特征1", "特征2"],
        "pose": "姿态",
        "expression": "表情"
    },
    "style": {
        "genre": "流派",
        "references": ["参考"],
        "mood": "情绪",
        "intensity": 0.8
    },
    "output": {
        "format": "image",
        "aspect_ratio": "1:1|16:9|9:16|4:3",
        "quality": "high|medium|low"
    },
    "constraints": {
        "must_include": [],
        "avoid": []
    }
}

融合规则：
1. 如果专家意见冲突，以视觉专家的主体描述为准，风格专家的风格判断为准
2. 情绪强度根据用户描述的强烈程度调整（很酷=0.9，稍微=0.3）
3. 确保所有字段都有值，不要留空"""

        user_prompt = f"用户原始输入: {user_input}\n\n专家输出:\n" + "\n".join(
            expert_summary) + "\n\n请融合为统一的IntentRepresentation。"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        intent_json = response.choices[0].message.content
        intent_dict = json.loads(intent_json)

        return IntentRepresentation.from_dict(intent_dict)