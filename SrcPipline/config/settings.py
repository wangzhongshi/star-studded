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