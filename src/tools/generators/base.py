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