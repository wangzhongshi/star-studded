import json
import re
import time
from typing import List, Dict, Any, Optional
from ..services.llm_client import deepseek_client
from ..config.settings import settings


def retry_on_json_error(max_retries=2, delay=1):
    """装饰器：JSON 解析失败时重试"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except json.JSONDecodeError as e:
                    if attempt < max_retries:
                        print(f"   ⚠️  JSON 解析失败，第 {attempt + 1} 次重试...")
                        time.sleep(delay)
                    else:
                        print(f"   ❌ 重试 {max_retries} 次后仍失败，返回默认调度")
                        return {
                            "experts": ["style", "mood"],
                            "reasoning": "DeepSeek 返回异常，fallback 到默认调度",
                            "mode": "normal"
                        }
            return None

        return wrapper

    return decorator


class SchedulerAgent:
    """
    调度智能体
    职责：分析用户输入，决定需要调用哪些专家
    支持：增量请求检测、意图模糊检测、多轮追问
    """

    def __init__(self):
        self.client = deepseek_client
        self.model = settings.DEEPSEEK.model_id

    @retry_on_json_error(max_retries=2, delay=1)
    def schedule(self, user_input: str, has_image: bool,
                 is_incremental: bool = False,
                 is_ambiguous: bool = False) -> Dict[str, Any]:
        """
        决定调用哪些专家
        """
        if is_incremental:
            return {
                "experts": [],
                "reasoning": "增量更新，基于上一次意图修改",
                "mode": "incremental"
            }

        if is_ambiguous:
            return {
                "experts": [],
                "reasoning": "意图模糊，需要追问",
                "mode": "clarification"
            }

        system_prompt = """你是一个调度智能体。你的任务是分析用户需求，决定需要调用哪些专家。

可用专家（使用短名）：
1. vision - 视觉分析专家（需要图片时调用）
2. style - 风格识别专家（分析艺术风格、流派、参考）
3. mood - 情绪氛围专家（分析情绪、叙事、氛围）

规则：
- 如果用户上传了图片，必须调用 vision
- 如果用户提到风格（如"赛博朋克""油画"），调用 style
- 如果用户提到情绪（如"温馨""悲伤""酷"），调用 mood
- 至少调用一个专家

重要：你的输出必须是JSON格式。

输出JSON格式：
{
    "experts": ["vision", "style", "mood"],
    "reasoning": "调度理由"
}"""

        user_prompt = f"用户输入: {user_input}\n是否上传图片: {has_image}\n\n请决定调用哪些专家。重要：你的输出必须是JSON格式。"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        raw = response.choices[0].message.content
        print(f"   [DEBUG] Raw response: {raw!r}")

        if not raw or not raw.strip():
            raise json.JSONDecodeError("Empty response", "", 0)

        result = json.loads(raw)
        result["mode"] = "normal"

        return result

    def generate_clarification_prompt(self, user_input: str, missing_info: List[str] = None) -> str:
        """
        生成追问提示（开放式，让用户自由输入补充）

        Args:
            user_input: 用户原始输入
            missing_info: 已知缺失的信息类型（可选）

        Returns:
            追问提示文本
        """
        system_prompt = """你是一个善于引导用户的AI助手。当用户意图不够明确时，你需要用友好、简洁的方式追问，帮助用户补充关键信息。

追问原则：
1. 每次只问最关键的1-2个问题
2. 不要给用户选项，让用户自由描述
3. 问题要具体，引导用户补充细节
4. 如果用户之前补充过，基于已有信息继续追问

输出格式：直接返回追问文本，不要JSON。"""

        # 构建上下文
        context = f"用户输入: {user_input}\n"
        if missing_info:
            context += f"已知缺失: {', '.join(missing_info)}\n"

        user_prompt = f"{context}\n\n请生成一个追问，帮助用户补充关键信息。追问要简洁（不超过30字），让用户自由输入回答。"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )

            prompt = response.choices[0].message.content.strip()
            # 去除引号
            prompt = prompt.strip('"\'')
            return prompt

        except Exception as e:
            print(f"   ⚠️  生成追问失败: {e}")
            # fallback 到默认追问
            return "能再详细描述一下你想要的画面吗？比如主体、风格、氛围等。"

    def analyze_missing_info(self, user_input: str) -> List[str]:
        """
        分析用户输入中缺失的关键信息

        Returns:
            缺失信息类型列表
        """
        missing = []

        # 检查主体
        if not self._has_subject(user_input):
            missing.append("主体")

        # 检查风格
        if not self._has_style(user_input):
            missing.append("风格")

        # 检查情绪/氛围
        if not self._has_mood(user_input):
            missing.append("氛围")

        # 检查细节
        if len(user_input) < 10:
            missing.append("细节")

        return missing

    def _has_subject(self, text: str) -> bool:
        """检查是否有明确主体"""
        # 简单启发式：是否有名词性描述
        subject_keywords = ["画", "生成", "创建", "做", "设计"]
        # 如果输入很短且没有具体描述，认为缺少主体
        if len(text) < 5:
            return False
        return True

    def _has_style(self, text: str) -> bool:
        """检查是否有风格描述"""
        style_keywords = ["风格", "风", "style", "油画", "水彩", "赛博朋克", "动漫", "写实", "卡通", "复古", "现代"]
        return any(kw in text for kw in style_keywords)

    def _has_mood(self, text: str) -> bool:
        """检查是否有情绪/氛围描述"""
        mood_keywords = ["氛围", "感觉", "情绪", "mood", "温馨", "冷酷", "梦幻", "神秘", "酷", "可爱", "恐怖", "浪漫"]
        return any(kw in text for kw in mood_keywords)

    def is_ambiguous(self, user_input: str) -> bool:
        """
        判断意图是否模糊（需要追问）

        规则：
        1. 输入长度 < 5
        2. 缺少主体
        3. 缺少风格和氛围
        4. 过于笼统（如"画张图""给我做个图片"）
        """
        # 过于简短的输入
        if len(user_input.strip()) < 5:
            return True

        # 过于笼统的输入
        vague_patterns = [
            r"^画[张个幅]?图$",
            r"^给我[画做].*图[片像]?$",
            r"^生成[张个幅]?图片$",
            r"^做[张个幅]?图$",
            r"^[搞来整].*[张个幅]?图$",
        ]
        for pattern in vague_patterns:
            if re.search(pattern, user_input.strip()):
                return True

        # 检查缺失关键信息
        missing = self.analyze_missing_info(user_input)
        # 如果缺失2项以上，认为模糊
        if len(missing) >= 2:
            return True

        return False

    def extract_image_path(self, user_input: str) -> tuple:
        """
        从输入中提取图片路径和真实消息
        """
        pattern = r'\[图片路径:\s*(.*?)\]\s*(.*)'
        match = re.match(pattern, user_input, re.DOTALL)

        if match:
            return match.group(1).strip(), match.group(2).strip()
        return None, user_input.strip()