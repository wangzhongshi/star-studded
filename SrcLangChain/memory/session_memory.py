from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from ..models.intent import IntentRepresentation


@dataclass
class SessionRecord:
    """单次交互记录"""
    timestamp: str
    user_input: str
    intent: IntentRepresentation
    image_url: str
    feedback: Optional[str] = None


class SessionMemory:
    """会话记忆管理"""

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.history: List[SessionRecord] = []
        self.current_context: Dict = {}

    def add_record(self, user_input: str, intent: IntentRepresentation,
                   image_url: str, feedback: Optional[str] = None):
        """添加记录"""
        record = SessionRecord(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            intent=intent,
            image_url=image_url,
            feedback=feedback
        )
        self.history.append(record)
        self.current_context = {
            "last_intent": intent.to_dict(),
            "last_image": image_url,
            "last_input": user_input
        }

    def get_last_intent(self) -> Optional[IntentRepresentation]:
        """获取上一次意图"""
        if not self.history:
            return None
        return self.history[-1].intent

    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        if not self.history:
            return ""

        last = self.history[-1]
        return f"""
上一次创作：
- 主题：{last.intent.subject.entity}
- 风格：{last.intent.style.genre}
- 情绪：{last.intent.style.mood}
- 强度：{last.intent.style.intensity}
- 用户反馈：{last.feedback or '无'}
"""

    def is_incremental_request(self, user_input: str) -> bool:
        """判断是否是增量请求"""
        incremental_keywords = [
            "再", "更", "稍微", "有点", "太", "不够",
            "酷一点", "暗一点", "亮一点", "换", "改",
            "像", "类似", "参考", "按照这个", "基于"
        ]
        return any(kw in user_input for kw in incremental_keywords)

    def is_ambiguous(self, user_input: str) -> bool:
        """判断意图是否模糊"""
        if len(user_input) < 10:
            return True

        has_subject = any(kw in user_input for kw in ["猫", "狗", "人", "风景", "建筑", "车", "花", "山", "海"])
        has_style = any(kw in user_input for kw in ["风格", "赛博朋克", "油画", "卡通", "写实", "动漫", "国风", "水墨"])

        return not (has_subject or has_style)

    def generate_follow_up_questions(self, user_input: str) -> List[str]:
        """生成追问问题"""
        questions = []

        if "画" in user_input and not any(
                kw in user_input for kw in ["猫", "狗", "人", "风景", "建筑", "车", "花", "山"]):
            questions.append("你想画什么主题？比如人物、动物、风景？")

        if not any(kw in user_input for kw in
                   ["风格", "赛博朋克", "油画", "卡通", "写实", "动漫", "国风", "水墨", "二次元"]):
            questions.append("想要什么风格？比如写实、卡通、赛博朋克、国风？")

        if not any(kw in user_input for kw in ["情绪", "氛围", "感觉", "酷", "温馨", "梦幻", "神秘", "悲伤", "开心"]):
            questions.append("想要什么样的氛围？比如酷炫、温馨、梦幻、神秘？")

        return questions[:2]

    def apply_incremental_update(self, user_input: str,
                                 last_intent: IntentRepresentation) -> IntentRepresentation:
        """应用增量更新"""
        import copy
        new_intent = copy.deepcopy(last_intent)

        # 强度调整
        if "更酷" in user_input or "酷一点" in user_input or "再酷" in user_input:
            new_intent.style.intensity = min(1.0, new_intent.style.intensity + 0.2)
        elif "稍微" in user_input or "有点" in user_input:
            new_intent.style.intensity = min(1.0, new_intent.style.intensity + 0.1)
        elif "太" in user_input and ("强" in user_input or "浓" in user_input or "过了" in user_input):
            new_intent.style.intensity = max(0.0, new_intent.style.intensity - 0.2)
        elif "淡" in user_input or "轻" in user_input:
            new_intent.style.intensity = max(0.0, new_intent.style.intensity - 0.1)

        # 风格切换
        if "换成" in user_input or "改" in user_input or "换成" in user_input:
            if "动漫" in user_input or "二次元" in user_input or "日漫" in user_input:
                new_intent.style.genre = "anime"
                new_intent.style.references = ["宫崎骏", "新海诚"]
            elif "写实" in user_input or "照片" in user_input:
                new_intent.style.genre = "realistic"
            elif "油画" in user_input or "古典" in user_input:
                new_intent.style.genre = "oil_painting"
                new_intent.style.references = ["梵高", "莫奈"]
            elif "国风" in user_input or "水墨" in user_input or "古风" in user_input:
                new_intent.style.genre = "chinese_ink"
                new_intent.style.references = ["水墨画", "山水画"]
            elif "赛博朋克" in user_input:
                new_intent.style.genre = "cyberpunk"
                new_intent.style.references = ["银翼杀手", "攻壳机动队"]

        # 情绪调整
        if "温馨" in user_input or "温暖" in user_input:
            new_intent.style.mood = "warm"
        elif "梦幻" in user_input or "唯美" in user_input:
            new_intent.style.mood = "dreamy"
        elif "神秘" in user_input or "暗黑" in user_input:
            new_intent.style.mood = "mysterious"
        elif "悲伤" in user_input or "忧郁" in user_input:
            new_intent.style.mood = "melancholic"
        elif "开心" in user_input or "欢乐" in user_input:
            new_intent.style.mood = "joyful"
        elif "酷炫" in user_input or "酷" in user_input:
            new_intent.style.mood = "cool"

        # 构图调整
        if "头像" in user_input or "方形" in user_input:
            new_intent.output.aspect_ratio = "1:1"
        elif "壁纸" in user_input or "横屏" in user_input or "电脑" in user_input:
            new_intent.output.aspect_ratio = "16:9"
        elif "手机" in user_input or "竖屏" in user_input:
            new_intent.output.aspect_ratio = "9:16"

        # 质量调整
        if "高清" in user_input or "高质量" in user_input or "超清" in user_input:
            new_intent.output.quality = "high"
        elif "草图" in user_input or "预览" in user_input:
            new_intent.output.quality = "low"

        # 添加约束
        if "不要" in user_input or "别" in user_input:
            # 提取不要的内容
            import re
            dont_match = re.search(r'不要(.+?)(?:，|。|$)', user_input)
            if dont_match:
                avoid_item = dont_match.group(1).strip()
                if avoid_item not in new_intent.constraints.avoid:
                    new_intent.constraints.avoid.append(avoid_item)

        return new_intent