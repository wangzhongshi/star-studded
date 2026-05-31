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
                        # 兜底：返回默认调度
                        return {
                            "experts": ["style", "mood"],
                            "reasoning": "DeepSeek 返回异常，fallback 到默认调度",
                            "mode": "normal"
                        }
            return None  # 理论上不会走到这里
        return wrapper
    return decorator


class SchedulerAgent:
    """
    调度智能体
    职责：分析用户输入，决定需要调用哪些专家
    支持：增量请求检测、意图模糊检测
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
                "experts": [],  # 增量更新跳过专家，直接融合
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

        # 空内容检查
        if not raw or not raw.strip():
            raise json.JSONDecodeError("Empty response", "", 0)

        result = json.loads(raw)
        result["mode"] = "normal"

        return result

    def extract_image_path(self, user_input: str) -> tuple:
        """
        从输入中提取图片路径和真实消息
        """
        pattern = r'\[图片路径:\s*(.*?)\]\s*(.*)'
        match = re.match(pattern, user_input, re.DOTALL)

        if match:
            return match.group(1).strip(), match.group(2).strip()
        return None, user_input.strip()