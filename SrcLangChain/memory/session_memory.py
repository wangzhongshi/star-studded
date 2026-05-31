from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from ..models.intent import IntentRepresentation


@dataclass
class SessionRecord:
    """单条会话记录"""
    user_input: str
    intent: Optional[IntentRepresentation] = None
    image_url: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    is_clarification: bool = False  # 是否是追问轮次


class SessionMemory:
    """
    会话记忆
    支持：增量更新、多轮追问、意图历史
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[SessionRecord] = []
        self.clarification_rounds: int = 0  # 追问轮次计数
        self.pending_intent: Optional[Dict[str, Any]] = None  # 待补充的意图片段
        self.max_clarification_rounds: int = 3  # 最大追问轮次

    def add_record(self, user_input: str, intent: IntentRepresentation = None,
                   image_url: str = None, is_clarification: bool = False):
        """添加记录"""
        record = SessionRecord(
            user_input=user_input,
            intent=intent,
            image_url=image_url,
            is_clarification=is_clarification
        )
        self.history.append(record)

        if is_clarification:
            self.clarification_rounds += 1

    def get_last_intent(self) -> Optional[IntentRepresentation]:
        """获取最后一次完整意图"""
        for record in reversed(self.history):
            if record.intent is not None:
                return record.intent
        return None

    def get_combined_input(self) -> str:
        """
        获取组合后的用户输入（包含追问补充）
        用于 Fusion 时整合多轮输入
        """
        # 过滤出非追问或包含有效信息的记录
        inputs = []
        for record in self.history:
            if not record.is_clarification or len(record.user_input) > 3:
                inputs.append(record.user_input)

        return "；".join(inputs)

    def is_incremental_request(self, user_input: str) -> bool:
        """检测是否是增量请求"""
        incremental_keywords = [
            "再", "更", "加", "换", "改", "变", "调整", "修改",
            "酷一点", "可爱一点", "亮一点", "暗一点",
            "换个", "改成", "变成", "不要", "去掉", "增加"
        ]
        return any(kw in user_input for kw in incremental_keywords)

    def is_ambiguous(self, user_input: str) -> bool:
        """
        检测意图是否模糊（结合历史追问次数）

        如果已经追问多次，不再追问，直接生成
        """
        # 如果已经追问太多次，不再追问
        if self.clarification_rounds >= self.max_clarification_rounds:
            return False

        # 如果历史已经有完整意图，当前输入可能是补充
        if self.get_last_intent() is not None:
            return False

        return True  # 由 Scheduler 进一步判断

    def generate_follow_up_questions(self, user_input: str) -> List[str]:
        """
        生成追问问题（改为返回追问提示，供前端展示输入框）

        返回：
            [追问提示文本] — 单元素列表，前端显示输入框
        """
        from ..agents.scheduler import SchedulerAgent
        scheduler = SchedulerAgent()

        # 分析缺失信息
        missing = scheduler.analyze_missing_info(user_input)

        # 生成追问提示
        prompt = scheduler.generate_clarification_prompt(user_input, missing)

        return [prompt]

    def can_generate(self) -> bool:
        """判断是否足够信息生成"""
        # 有完整意图，或追问次数已达上限
        return self.get_last_intent() is not None or \
            self.clarification_rounds >= self.max_clarification_rounds

    def reset_clarification(self):
        """重置追问状态（新会话开始时）"""
        self.clarification_rounds = 0
        self.pending_intent = None