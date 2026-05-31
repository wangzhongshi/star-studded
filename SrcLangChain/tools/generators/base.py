from abc import ABC, abstractmethod
from ...models.intent import IntentRepresentation


class BaseGenerator(ABC):
    """生成器基类"""

    @abstractmethod
    def translate(self, intent: IntentRepresentation) -> str:
        """将意图翻译为模型专用提示词"""
        pass

    @abstractmethod
    def generate(self, intent: IntentRepresentation) -> str:
        """调用API生成，返回图片URL"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """生成器名称"""
        pass

    @property
    @abstractmethod
    def strengths(self) -> list:
        """擅长领域"""
        pass