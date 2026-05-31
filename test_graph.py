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

from src.graph.workflow import app, get_or_create_memory


def create_initial_state(user_input: str, session_id: str = "default") -> dict:
    return {
        "user_input": user_input,
        "session_id": session_id,
        "image_path": None,
        "has_image": False,
        "scheduled_experts": [],
        "expert_outputs": [],
        "fused_intent": None,
        "selected_model": None,
        "final_prompt": None,      # ← 新增：PromptEngineer 输出
        "prompt_meta": None,       # ← 新增：提示词元数据
        "final_output": None,
        "error": None,
        "mode": None,
        "questions": None
    }


def test_normal():
    """测试正常流程"""
    print("=" * 60)
    print("测试1: 正常流程（纯文本）")
    print("=" * 60)

    state = create_initial_state("给我家猫画个赛博朋克头像，要很酷", "test_normal")
    result = app.invoke(state)

    print(f"\n{'=' * 60}")
    if result.get("final_output"):
        print(f"✅ 成功:")
        print(f"   {result['final_output']}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print(f"{'=' * 60}")

    return result


def test_with_image(image_path: str):
    """测试带图片"""
    print("\n" + "=" * 60)
    print("测试2: 带图片输入")
    print("=" * 60)

    state = create_initial_state(
        f"[图片路径: {image_path}] 把这张图换成赛博朋克风格，要很酷",
        "test_image"
    )
    result = app.invoke(state)

    print(f"\n{'=' * 60}")
    if result.get("final_output"):
        print(f"✅ 成功:")
        print(f"   {result['final_output']}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print(f"{'=' * 60}")

    return result


def test_incremental():
    """测试增量更新（迭代优化）"""
    print("\n" + "=" * 60)
    print("测试3: 增量更新（会话记忆）")
    print("=" * 60)

    session_id = "test_incremental"

    # 第一次请求
    print("\n--- 第1轮: 生成基础图像 ---")
    state1 = create_initial_state("给我家猫画个赛博朋克头像，要很酷", session_id)
    result1 = app.invoke(state1)
    print(f"图像1:")
    print(f"   {result1.get('final_output', '失败')}")

    # 第二次请求：增量更新
    print("\n--- 第2轮: 再酷一点 ---")
    state2 = create_initial_state("再酷一点，加霓虹灯", session_id)
    result2 = app.invoke(state2)
    print(f"图像2:")
    print(f"   {result2.get('final_output', '失败')}")

    # 第三次请求：风格切换
    print("\n--- 第3轮: 换成动漫风 ---")
    state3 = create_initial_state("换成动漫风", session_id)
    result3 = app.invoke(state3)
    print(f"图像3:")
    print(f"   {result3.get('final_output', '失败')}")

    # 查看会话历史
    memory = get_or_create_memory(session_id)
    print(f"\n--- 会话历史 ({len(memory.history)} 条) ---")
    for i, record in enumerate(memory.history):
        print(f"  {i + 1}. {record.user_input[:40]}...")
        print(f"      -> {record.image_url}")

    return result3


def test_clarification():
    """测试主动交互（意图模糊）"""
    print("\n" + "=" * 60)
    print("测试4: 主动交互（意图模糊）")
    print("=" * 60)

    # 第一次：模糊输入
    print("\n--- 用户输入: '给我画张图' ---")
    state1 = create_initial_state("给我画张图", "test_clarification")
    result1 = app.invoke(state1)

    if result1.get("mode") == "clarification":
        print(f"✅ 系统追问: {result1.get('questions')}")
        print(f"   未生成图像（正确行为）")
        print(f"   final_output: {result1.get('final_output')}")  # 应该是 None

        # 模拟用户回答
        follow_up = "画一只猫，赛博朋克风格，要酷炫"
        print(f"\n--- 用户回答: '{follow_up}' ---")

        state2 = create_initial_state(follow_up, "test_clarification")
        result2 = app.invoke(state2)

        print(f"\n{'=' * 60}")
        if result2.get("final_output"):
            print(f"✅ 最终生成:")
            print(f"   {result2['final_output']}")
        else:
            print(f"❌ 失败: {result2.get('error')}")
        print(f"{'=' * 60}")

        return result2
    else:
        print(f"⚠️  未触发追问，直接生成:")
        print(f"   {result1.get('final_output', '失败')}")
        return result1


# ==================== 新增测试函数 ====================

def test_prompt_engineer():
    """测试 PromptEngineer 提示词质量"""
    print("\n" + "=" * 60)
    print("测试5: PromptEngineer 提示词质量")
    print("=" * 60)

    test_cases = [
        "给我家猫画个赛博朋克头像，要很酷",
        "古风女子，胶片复古风格，午后暖阳",
        "电影感 portrait，85mm，逆光，青橙色调",
        "动漫风格，战斗场景，高饱和色彩",
        "写实肖像，专业摄影，自然光"
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n--- 用例 {i}: {user_input} ---")
        state = create_initial_state(user_input, f"test_pe_{i}")
        result = app.invoke(state)

        if result.get("final_prompt"):
            print(f"✅ 提示词:")
            # 打印完整提示词（不分段）
            print(f"   {result['final_prompt']}")
            print(f"\n📊 元数据:")
            meta = result.get("prompt_meta", {})
            print(f"   摄影: {meta.get('photo', {})}")
            print(f"   光影: {meta.get('lighting', {})}")
            print(f"   构图: {meta.get('composition', {})}")
            print(f"   色彩: {meta.get('color', {})}")
            print(f"   叙事: {meta.get('narrative', 'N/A')}")
        else:
            print(f"❌ 未生成提示词: {result.get('error')}")

    return result


def test_prompt_engineer_vs_fallback():
    """对比 PromptEngineer vs 原始 translate 的提示词质量"""
    print("\n" + "=" * 60)
    print("测试6: PromptEngineer vs Fallback 对比")
    print("=" * 60)

    from src.tools.generators.seedream import SeedreamGenerator
    from src.models.intent import IntentRepresentation, Subject, Style, Output, Constraints

    # 构造一个意图
    intent = IntentRepresentation(
        subject=Subject(
            entity="古风女子",
            attributes=["长发", "竹叶发饰"],
            pose="侧身回眸",
            expression="淡然微笑"
        ),
        style=Style(
            genre="赛博朋克",
            references=["银翼杀手", "攻壳机动队"],
            mood="神秘",
            intensity=0.8
        ),
        output=Output(format="image", aspect_ratio="9:16", quality="high"),
        constraints=Constraints(must_include=["霓虹灯光", "雨夜"], avoid=["现代建筑"])
    )

    # Fallback 提示词（原始 translate）
    generator = SeedreamGenerator()
    fallback_prompt = generator.translate(intent)

    # PromptEngineer 提示词（走完整流程）
    state = create_initial_state("古风女子赛博朋克风格，要很酷", "test_compare")
    result = app.invoke(state)
    pe_prompt = result.get("final_prompt", "N/A")

    print(f"\n--- 原始 Fallback ---")
    print(f"长度: {len(fallback_prompt)} 字")
    print(f"内容: {fallback_prompt}")

    print(f"\n--- PromptEngineer ---")
    print(f"长度: {len(pe_prompt) if pe_prompt != 'N/A' else 'N/A'} 字")
    print(f"内容: {pe_prompt}")

    print(f"\n--- 对比 ---")
    if pe_prompt != "N/A":
        print(f"PromptEngineer 比 Fallback 多: {len(pe_prompt) - len(fallback_prompt)} 字")
        print(f"新增维度: 摄影参数、光影细节、构图法则、色彩科学、叙事描述")

    return result


def test_style_coverage():
    """测试风格映射表覆盖度"""
    print("\n" + "=" * 60)
    print("测试7: 风格映射表覆盖度")
    print("=" * 60)

    from src.agents.experts.prompt_engineer import PromptEngineer

    engineer = PromptEngineer()
    styles = list(engineer.style_map.keys())

    print(f"已配置风格 ({len(styles)} 种):")
    for i, style in enumerate(styles, 1):
        print(f"  {i}. {style}")

    test_styles = [
        "赛博朋克", "胶片复古", "电影感", "动漫", "写实肖像",
        "暗黑奇幻", "日系清新", "蒸汽朋克", "水墨风", "油画"
    ]

    print(f"\n测试匹配:")
    for style in test_styles:
        config = engineer._match_style(style)
        status = "✅" if config else "❌"
        print(f"  {status} {style}: {'命中' if config else '未命中（用默认）'}")

    return styles


def test_prompt_engineer_direct():
    """直接测试 PromptEngineer（不走完整 workflow）"""
    print("\n" + "=" * 60)
    print("测试8: PromptEngineer 单元测试")
    print("=" * 60)

    from src.agents.experts.prompt_engineer import PromptEngineer
    from src.models.intent import IntentRepresentation, Subject, Style, Output, Constraints

    engineer = PromptEngineer()

    test_cases = [
        {
            "name": "赛博朋克猫",
            "intent": IntentRepresentation(
                subject=Subject(entity="猫", attributes=["机械义眼"], pose="蹲坐", expression="冷酷"),
                style=Style(genre="赛博朋克", references=["银翼杀手"], mood="酷炫", intensity=0.9),
                output=Output(quality="high"),
                constraints=Constraints(must_include=["霓虹灯"])
            )
        },
        {
            "name": "胶片复古人像",
            "intent": IntentRepresentation(
                subject=Subject(entity="少女", attributes=["麻花辫"], pose="托腮", expression="温柔"),
                style=Style(genre="胶片复古", mood="怀旧", intensity=0.6),
                output=Output(quality="high"),
                constraints=Constraints()
            )
        },
        {
            "name": "电影感风景",
            "intent": IntentRepresentation(
                subject=Subject(entity="雪山", attributes=["日出", "云海"]),
                style=Style(genre="电影感", references=["国家地理"], mood="壮阔", intensity=0.8),
                output=Output(aspect_ratio="16:9", quality="high"),
                constraints=Constraints()
            )
        }
    ]

    for case in test_cases:
        print(f"\n--- 用例: {case['name']} ---")
        result = engineer.design(case["intent"])
        prompt = result["prompt"]
        meta = result["meta"]

        print(f"提示词 ({len(prompt)} 字):")
        print(f"  {prompt[:150]}...")
        print(f"元数据:")
        print(f"  焦段: {meta.photo.focal_length}, 光圈: {meta.photo.aperture}")
        print(f"  光影: {meta.lighting.direction}, 氛围: {meta.lighting.atmosphere}")
        print(f"  构图: {meta.composition.shot_size}, {meta.composition.rule}")
        print(f"  叙事: {meta.narrative[:50]}...")

    return result


if __name__ == "__main__":
    # 原有测试
    # test_normal()
    # test_with_image(r"E:\壁纸\1089-2023-10-08050345-1696755825662.jpg")
    # test_incremental()
    # test_clarification()

    # 新增测试
    # test_prompt_engineer()
    test_prompt_engineer_vs_fallback()
    # test_style_coverage()
    # test_prompt_engineer_direct()