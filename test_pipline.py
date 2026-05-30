import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent/'src'))

import os
import sys

# 设置环境变量
os.environ["DEEPSEEK_API_KEY"] = "your_api_key"
os.environ["DASHSCOPE_API_KEY"] = "your_api_key"
os.environ["ARK_API_KEY"] = "your_api_key"

sys.path.append("src")

from src.agents.intent_parser import IntentParser
from src.agents.vision_analyzer import VisionAnalyzer
from src.agents.adapters.seedream import SeedreamAdapter


def test_text_only():
    """测试纯文本输入"""
    print("=" * 60)
    print("测试1: 纯文本输入")
    print("=" * 60)

    parser = IntentParser()
    intent = parser.parse("给我家猫画个赛博朋克头像，要很酷")

    print(f"意图: {intent.to_dict()}")

    adapter = SeedreamAdapter()
    prompt = adapter.translate(intent)
    print(f"\n提示词: {prompt}")

    # 生成图像
    print("\n生成中...")
    image_url = adapter.generate(intent)
    print(f"图像URL: {image_url}")

    return image_url


def test_with_image(image_path: str):
    """测试带图片输入"""
    print("\n" + "=" * 60)
    print("测试2: 带图片输入")
    print("=" * 60)

    # 1. 视觉分析
    print("Step 1: 视觉分析...")
    vision = VisionAnalyzer()
    description = vision.describe(image_path)
    print(f"图像描述: {description[:200]}...")

    # 2. 意图解析
    print("\nStep 2: 意图解析...")
    parser = IntentParser()
    intent = parser.parse(
        "把这张图换成赛博朋克风格，要很酷",
        image_description=description
    )
    print(f"意图: {intent.to_dict()}")

    # 3. 生成图像
    print("\nStep 3: 生成图像...")
    adapter = SeedreamAdapter()
    prompt = adapter.translate(intent)
    print(f"提示词: {prompt}")

    image_url = adapter.generate(intent)
    print(f"图像URL: {image_url}")

    return image_url


def test_reverse_prompt(image_path: str):
    """测试反推提示词"""
    print("\n" + "=" * 60)
    print("测试3: 反推提示词")
    print("=" * 60)

    vision = VisionAnalyzer()
    prompt = vision.reverse_prompt(image_path)
    print(f"反推提示词: {prompt}")

    return prompt


if __name__ == "__main__":
    # 测试1: 纯文本
    # test_text_only()

    # 测试2: 带图片（需要本地图片路径）
    # test_with_image(r"E:\壁纸\1089-2023-10-08050345-1696755825662.jpg")

    # 测试3: 反推
    test_reverse_prompt(r"E:\壁纸\1089-2023-10-08050345-1696755825662.jpg")