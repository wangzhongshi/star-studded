import os
import sys

os.environ["DEEPSEEK_API_KEY"] = "your-api-key"
os.environ["DASHSCOPE_API_KEY"] = "your-api-key"
os.environ["ARK_API_KEY"] = "your-api-key"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from SrcLangChain.graph.workflow import app, get_or_create_memory


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


if __name__ == "__main__":
    # 选择测试
    # test_normal()
    # test_with_image(r"E:\壁纸\1089-2023-10-08050345-1696755825662.jpg")
    # test_incremental()
    test_clarification()