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
import sys


os.environ["DEEPSEEK_API_KEY"] = "your-api-key"
os.environ["DASHSCOPE_API_KEY"] = "your-api-key"
os.environ["ARK_API_KEY"] = "your-api-key"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from SrcPipline.agents.orchestrator import create_orchestrator


def test_text_only():
    print("测试1: 纯文本输入")
    agent = create_orchestrator()
    result = agent.invoke("给我家猫画个赛博朋克头像，要很酷")

    print(f"\n最终结果: {result['output'][:100]}...")
    return result


def test_with_image(image_path: str):
    print("\n测试2: 带图片输入")
    agent = create_orchestrator()
    result = agent.invoke(f"[图片路径: {image_path}] 把这张图换成赛博朋克风格，要很酷")

    print(f"\n最终结果: {result['output'][:100]}...")
    return result


if __name__ == "__main__":
    test_text_only()
    # test_with_image(r"E:\壁纸\1089-2023-10-08050345-1696755825662.jpg")