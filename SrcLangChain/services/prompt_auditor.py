import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AuditResult:
    """审查结果"""
    passed: bool          # 是否通过
    result_code: int      # 0-拦截 1-通过 2-警告
    risk_score: int       # 0-100
    risk_type: Optional[str]  # 风险类型
    blocked_keywords: List[str]  # 命中关键词
    message: str          # 审查说明
    processed_prompt: str # 处理后的提示词（清洗后）


class PromptAuditor:
    """
    提示词审查器
    职责：后端基础审查，防止恶意攻击
    """

    # 黑名单关键词（基础）
    BLACKLIST = [
        # NSFW
        "nude", "naked", "porn", "sex", "nsfw", "explicit", "xxx",
        "裸体", "裸照", "色情", "性", "裸露", "淫秽",
        # 暴力
        "violence", "gore", "blood", "kill", "murder", "death", "torture",
        "暴力", "血腥", "杀人", "死亡", "虐待", "自残", "自杀",
        # 政治敏感（简化版，后续扩展）
        "terrorist", "bomb", "attack", "爆炸", "恐怖袭击",
        # Prompt Injection 特征
        "ignore previous", "forget above", "system prompt", "override",
        "忽略上文", "忘记前面", "系统提示", "覆盖设置",
    ]

    # 长度限制
    MAX_LENGTH = 2000
    MIN_LENGTH = 2

    # 重复字符阈值
    MAX_REPEAT = 50

    # 特殊字符比例阈值
    MAX_SPECIAL_RATIO = 0.3

    def __init__(self):
        self.blacklist_pattern = re.compile(
            r'(' + '|'.join(re.escape(k) for k in self.BLACKLIST) + r')',
            re.IGNORECASE
        )

    def audit(self, prompt: str) -> AuditResult:
        """
        审查提示词
        """
        if not prompt:
            return AuditResult(
                passed=False,
                result_code=0,
                risk_score=100,
                risk_type="empty_prompt",
                blocked_keywords=[],
                message="提示词为空",
                processed_prompt=""
            )

        # 1. 长度检查
        length_check = self._check_length(prompt)
        if not length_check[0]:
            return AuditResult(
                passed=False,
                result_code=0,
                risk_score=80,
                risk_type="length_violation",
                blocked_keywords=[],
                message=length_check[1],
                processed_prompt=prompt[:self.MAX_LENGTH]
            )

        # 2. 黑名单检查
        blacklist_check = self._check_blacklist(prompt)
        if blacklist_check[0]:
            return AuditResult(
                passed=False,
                result_code=0,
                risk_score=90,
                risk_type="blacklist",
                blocked_keywords=blacklist_check[1],
                message=f"命中黑名单关键词: {', '.join(blacklist_check[1])}",
                processed_prompt=self._clean_prompt(prompt, blacklist_check[1])
            )

        # 3. 重复字符检查
        repeat_check = self._check_repetition(prompt)
        if not repeat_check[0]:
            return AuditResult(
                passed=False,
                result_code=0,
                risk_score=70,
                risk_type="repetition_attack",
                blocked_keywords=[],
                message=repeat_check[1],
                processed_prompt=prompt
            )

        # 4. 特殊字符比例检查
        special_check = self._check_special_chars(prompt)
        if not special_check[0]:
            return AuditResult(
                passed=False,
                result_code=0,
                risk_score=60,
                risk_type="special_chars",
                blocked_keywords=[],
                message=special_check[1],
                processed_prompt=prompt
            )

        # 5. 警告：提示词过长但未超限
        risk_score = 0
        risk_type = None
        message = "审查通过"

        if len(prompt) > 1500:
            risk_score = 20
            risk_type = "long_prompt"
            message = "提示词较长，建议精简"

        # 清洗：去除多余空格
        processed = self._normalize_prompt(prompt)

        return AuditResult(
            passed=True,
            result_code=1 if risk_score == 0 else 2,
            risk_score=risk_score,
            risk_type=risk_type,
            blocked_keywords=[],
            message=message,
            processed_prompt=processed
        )

    def _check_length(self, prompt: str) -> Tuple[bool, str]:
        """长度检查"""
        if len(prompt) < self.MIN_LENGTH:
            return False, f"提示词过短（{len(prompt)} 字符），最少 {self.MIN_LENGTH} 字符"
        if len(prompt) > self.MAX_LENGTH:
            return False, f"提示词过长（{len(prompt)} 字符），最多 {self.MAX_LENGTH} 字符"
        return True, ""

    def _check_blacklist(self, prompt: str) -> Tuple[bool, List[str]]:
        """黑名单检查"""
        matches = self.blacklist_pattern.findall(prompt)
        if matches:
            # 去重
            unique_matches = list(set(m.lower() for m in matches))
            return True, unique_matches
        return False, []

    def _check_repetition(self, prompt: str) -> Tuple[bool, str]:
        """重复字符检查"""
        # 检查连续重复字符
        for char in set(prompt):
            if char * self.MAX_REPEAT in prompt:
                return False, f"检测到重复字符攻击（'{char}' 重复 {self.MAX_REPEAT} 次以上）"
        return True, ""

    def _check_special_chars(self, prompt: str) -> Tuple[bool, str]:
        """特殊字符比例检查"""
        # 统计非中文、非英文、非数字、非常见标点的字符
        special_chars = re.findall(r'[^a-zA-Z0-9\u4e00-\u9fa5\s，。！？、：""''（）【】《》]', prompt)
        if len(prompt) > 0:
            ratio = len(special_chars) / len(prompt)
            if ratio > self.MAX_SPECIAL_RATIO:
                return False, f"特殊字符比例过高（{ratio:.1%}），可能存在注入攻击"
        return True, ""

    def _clean_prompt(self, prompt: str, blocked_keywords: List[str]) -> str:
        """清洗提示词（替换黑名单词为***）"""
        result = prompt
        for keyword in blocked_keywords:
            result = re.sub(re.escape(keyword), '***', result, flags=re.IGNORECASE)
        return result

    def _normalize_prompt(self, prompt: str) -> str:
        """规范化提示词"""
        # 去除多余空格
        result = re.sub(r'\s+', ' ', prompt)
        # 去除首尾空格
        return result.strip()


# 全局实例
auditor = PromptAuditor()