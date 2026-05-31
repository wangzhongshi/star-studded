import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    name: str
    model_id: str
    api_key: str
    base_url: str


class Settings:
    # DeepSeek 意图解析
    DEEPSEEK = ModelConfig(
        name="deepseek",
        model_id="deepseek-v4-pro",
        api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        base_url="https://api.deepseek.com"
    )

    # 百炼 Qwen3.6 视觉理解
    QWEN = ModelConfig(
        name="qwen",
        model_id="qwen3.6-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY", ""),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    # 豆包 Seedream-5.0
    DOUBAO = ModelConfig(
        name="doubao",
        model_id="doubao-seedream-5-0-260128",
        api_key=os.getenv("ARK_API_KEY", ""),
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )


settings = Settings()