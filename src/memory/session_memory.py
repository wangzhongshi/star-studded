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
    支持：增量更新、多轮追问（最多6轮）、意图历史
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[SessionRecord] = []
        self.clarification_rounds: int = 0  # 已完成的追问轮次
        self.max_clarification_rounds: int = 6  # 最大追问轮次
        self.pending_intent: Optional[Dict[str, Any]] = None  # 待补充的意图片段
        self.last_question: Optional[str] = None  # 上一次追问的问题

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
        inputs = []
        for record in self.history:
            # 只取有效输入（非空且长度>0）
            text = record.user_input.strip()
            if text:
                inputs.append(text)

        return "；".join(inputs)

    def get_clarification_history(self) -> List[Dict[str, str]]:
        """
        获取追问历史（问题->回答）
        用于生成更精准的追问
        """
        history = []
        for i, record in enumerate(self.history):
            if record.is_clarification:
                # 找到对应的追问问题（前一个记录如果是系统追问，则配对）
                if i > 0 and not self.history[i-1].is_clarification:
                    history.append({
                        "question": self.history[i-1].user_input,  # 系统问题
                        "answer": record.user_input  # 用户回答
                    })
        return history

    def is_incremental_request(self, user_input: str) -> bool:
        """检测是否是增量请求"""
        incremental_keywords = [
            "再", "更", "加", "换", "改", "变", "调整", "修改",
            "酷一点", "可爱一点", "亮一点", "暗一点",
            "换个", "改成", "变成", "不要", "去掉", "增加"
        ]
        return any(kw in user_input for kw in incremental_keywords)

    def should_ask_clarification(self, user_input: str) -> bool:
        """
        判断是否需要继续追问

        规则：
        1. 已达最大追问次数 -> 不追问，强制生成
        2. 历史已有完整意图 -> 不追问
        3. 由 Scheduler 进一步判断内容是否模糊
        """
        # 已达上限，强制生成
        if self.clarification_rounds >= self.max_clarification_rounds:
            return False

        # 已有完整意图
        if self.get_last_intent() is not None:
            return False

        return True

    def generate_follow_up_questions(self, user_input: str) -> List[str]:
        """
        生成追问问题（开放式，供前端展示输入框）

        返回：
            [追问提示文本] — 单元素列表，前端显示输入框
        """
        from ..agents.scheduler import SchedulerAgent
        scheduler = SchedulerAgent()

        # 分析缺失信息（基于合并后的完整输入）
        combined = self.get_combined_input()
        missing = scheduler.analyze_missing_info(combined)

        # 生成追问提示
        prompt = scheduler.generate_clarification_prompt(combined, missing)

        self.last_question = prompt
        return [prompt]

    def get_remaining_rounds(self) -> int:
        """获取剩余可追问次数"""
        return max(0, self.max_clarification_rounds - self.clarification_rounds)

    def can_generate(self) -> bool:
        """判断是否足够信息生成"""
        # 有完整意图，或追问次数已达上限
        return self.get_last_intent() is not None or \
            self.clarification_rounds >= self.max_clarification_rounds

    def reset_clarification(self):
        """重置追问状态（新会话开始时）"""
        self.clarification_rounds = 0
        self.pending_intent = None
        self.last_question = None