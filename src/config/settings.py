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
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DeepSeekConfig:
    api_key: str = ""
    model_id: str = "deepseek-v4-pro"
    base_url: str = "https://api.deepseek.com/v1"

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.environ.get("DEEPSEEK_API_KEY", "")


@dataclass
class QwenConfig:
    api_key: str = ""
    model_id: str = "qwen3.6-plus"
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")


@dataclass
class DoubaoConfig:
    api_key: str = ""
    model_id: str = "doubao-seedream-5-0-260128"
    base_url: str = "https://ark.cn-beijing.volces.com/api/v3"

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.environ.get("ARK_API_KEY", "")


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = "123456"
    name: str = "renwei"

    def __post_init__(self):
        self.host = os.environ.get("DB_HOST", self.host)
        self.port = int(os.environ.get("DB_PORT", str(self.port)))
        self.user = os.environ.get("DB_USER", self.user)
        self.password = os.environ.get("DB_PASSWORD", self.password)
        self.name = os.environ.get("DB_NAME", self.name)

    @property
    def url(self) -> str:
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?charset=utf8mb4"


class Settings:
    def __init__(self):
        self.DEEPSEEK = DeepSeekConfig()
        self.QWEN = QwenConfig()
        self.DOUBAO = DoubaoConfig()
        self.DATABASE = DatabaseConfig()
        self.SECRET_KEY = os.environ.get("RENWEI_SECRET_KEY", "")


# 延迟初始化：使用时才创建实例
_settings = None

def get_settings():
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# 兼容旧代码
settings = get_settings()