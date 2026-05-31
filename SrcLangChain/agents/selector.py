from typing import Dict, Any
from ..models.intent import IntentRepresentation


class SelectorAgent:
    """
    选择智能体
    职责：根据意图选择最优生成模型
    """

    def __init__(self):
        # 模型注册表
        self.models = {
            "seedream": {
                "name": "豆包Seedream-5.0",
                "strengths": ["photo_realistic", "chinese_prompt", "fast", "general"],
                "cost": 0.05,
                "speed": 3
            },
            "wanxiang": {
                "name": "通义万相",
                "strengths": ["chinese_style", "traditional", "ink_wash"],
                "cost": 0.08,
                "speed": 5
            }
        }

    def select(self, intent: IntentRepresentation) -> Dict[str, Any]:
        """
        选择最优模型
        """
        scores = {}

        for model_id, model_info in self.models.items():
            score = 0

            # 能力匹配
            genre = intent.style.genre.lower()
            if genre in ["赛博朋克", "cyberpunk", "科幻", "写实", "照片"]:
                if "photo_realistic" in model_info["strengths"]:
                    score += 3

            if genre in ["国风", "水墨", "传统"]:
                if "chinese_style" in model_info["strengths"]:
                    score += 3

            # 质量需求
            if intent.output.quality == "high":
                score += 1

            # 默认偏好
            if model_id == "seedream":
                score += 1  # Demo阶段优先Seedream

            scores[model_id] = score

        # 选最高分
        best_model = max(scores, key=scores.get)

        return {
            "selected_model": best_model,
            "model_name": self.models[best_model]["name"],
            "scores": scores,
            "reasoning": f"基于风格'{intent.style.genre}'选择{self.models[best_model]['name']}"
        }