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


@dataclass
class ModelConfig:
    name: str
    model_id: str


class Settings:
    # DeepSeek 意图解析
    DEEPSEEK = ModelConfig(
        name="deepseek",
        model_id="deepseek-v4-pro"  # 你的实际模型ID
    )

    # 百炼 Qwen3.6 视觉理解
    QWEN = ModelConfig(
        name="qwen",
        model_id="qwen3.6-plus"  # 你的实际模型ID
    )

    # 豆包 Seedream-5.0
    DOUBAO = ModelConfig(
        name="doubao",
        model_id="doubao-seedream-5-0-260128"
    )


settings = Settings()