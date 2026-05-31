from typing import Dict, List, Any, Optional, TypedDict, Annotated
import json
from langgraph.graph import StateGraph, END

from ..models.intent import IntentRepresentation
from ..agents.scheduler import SchedulerAgent
from ..agents.experts.vision_expert import VisionExpert
from ..agents.experts.style_expert import StyleExpert
from ..agents.experts.mood_expert import MoodExpert
from ..agents.experts.prompt_engineer import PromptEngineer
from ..agents.fusion import FusionAgent
from ..agents.selector import SelectorAgent
from ..agents.generator import GeneratorAgent
from ..memory.session_memory import SessionMemory



# 自定义合并函数
def merge_expert_outputs(left: List[Dict], right: List[Dict]) -> List[Dict]:
    return left + right


def merge_errors(left: Optional[str], right: Optional[str]) -> Optional[str]:
    if left and right:
        return f"{left}; {right}"
    return left or right


# 全局会话存储
session_memories: Dict[str, SessionMemory] = {}


def get_or_create_memory(session_id: str) -> SessionMemory:
    if session_id not in session_memories:
        session_memories[session_id] = SessionMemory(session_id)
    return session_memories[session_id]


# 定义状态
class GraphState(TypedDict):
    user_input: str
    session_id: str
    image_path: Optional[str]
    has_image: bool
    scheduled_experts: List[str]
    expert_outputs: Annotated[List[Dict[str, Any]], merge_expert_outputs]
    fused_intent: Optional[IntentRepresentation]
    selected_model: Optional[str]
    final_prompt: Optional[str]           # ← 新增：PromptEngineer 输出的提示词
    prompt_meta: Optional[Dict]           # ← 新增：提示词元数据（创作回放用）
    final_output: Optional[str]
    error: Annotated[Optional[str], merge_errors]
    mode: Optional[str]  # normal | incremental | clarification
    questions: Optional[List[str]]


# 初始化智能体
scheduler = SchedulerAgent()
vision_expert = VisionExpert()
style_expert = StyleExpert()
mood_expert = MoodExpert()
fusion_agent = FusionAgent()
selector = SelectorAgent()
prompt_engineer = PromptEngineer()      # ← 新增
generator = GeneratorAgent()


def node_scheduler(state: GraphState) -> Dict[str, Any]:
    """调度节点"""
    print(f"\n{'=' * 60}")
    print(f"🔀 [Scheduler] 分析用户需求")
    print(f"{'=' * 60}")
    print(f"   用户输入: {state['user_input'][:60]}...")

    # 提取图片路径
    image_path, message = scheduler.extract_image_path(state["user_input"])
    has_image = image_path is not None

    print(f"   图片路径: {image_path}")
    print(f"   提取消息: {message[:60]}...")

    # 获取会话记忆
    session_id = state.get("session_id", "default")
    memory = get_or_create_memory(session_id)

    # 检查是否是增量请求
    is_incremental = memory.is_incremental_request(message)
    if is_incremental and memory.get_last_intent():
        print(f"   📈 检测到增量请求，基于上一次意图修改")
        return {
            "image_path": image_path,
            "has_image": has_image,
            "user_input": message,
            "mode": "incremental",
            "questions": None
        }

    # 检查意图是否模糊
    is_ambiguous = memory.is_ambiguous(message)
    if is_ambiguous:
        print(f"   ❓ 意图模糊，需要追问")
        questions = memory.generate_follow_up_questions(message)
        print(f"   追问: {questions}")
        return {
            "image_path": image_path,
            "has_image": has_image,
            "user_input": message,
            "mode": "clarification",
            "questions": questions,
            "scheduled_experts": []  # 不调度任何专家
        }

    # 正常调度
    schedule_result = scheduler.schedule(message, has_image)
    experts = schedule_result.get("experts", [])

    print(f"   ✅ 调度结果: 调用 {', '.join(experts)}")

    return {
        "image_path": image_path,
        "has_image": has_image,
        "user_input": message,
        "scheduled_experts": experts,
        "mode": "normal",
        "questions": None
    }


def node_vision(state: GraphState) -> Dict[str, Any]:
    """视觉专家节点"""
    if "vision" not in state.get("scheduled_experts", []):
        return {"expert_outputs": []}

    if not state.get("image_path"):
        return {"expert_outputs": []}

    print(f"\n👁️  [VisionExpert] 分析图像...")
    try:
        result = vision_expert.analyze(state["image_path"])
        print(f"   ✅ 完成: {result['output'].get('subject', 'N/A')[:50]}...")
        return {"expert_outputs": [result]}
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return {"error": str(e), "expert_outputs": []}


def node_style(state: GraphState) -> Dict[str, Any]:
    """风格专家节点"""
    if "style" not in state.get("scheduled_experts", []):
        return {"expert_outputs": []}

    print(f"\n🎨 [StyleExpert] 分析风格...")

    vision_desc = ""
    for output in state.get("expert_outputs", []):
        if output.get("expert") == "vision":
            vision_desc = json.dumps(output["output"], ensure_ascii=False)

    try:
        result = style_expert.analyze(state["user_input"], vision_desc)
        print(f"   ✅ 完成: {result['output'].get('genre', 'N/A')}")
        return {"expert_outputs": [result]}
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return {"error": str(e), "expert_outputs": []}


def node_mood(state: GraphState) -> Dict[str, Any]:
    """情绪专家节点"""
    if "mood" not in state.get("scheduled_experts", []):
        return {"expert_outputs": []}

    print(f"\n💭 [MoodExpert] 分析情绪...")

    vision_desc = ""
    for output in state.get("expert_outputs", []):
        if output.get("expert") == "vision":
            vision_desc = json.dumps(output["output"], ensure_ascii=False)

    try:
        result = mood_expert.analyze(state["user_input"], vision_desc)
        print(f"   ✅ 完成: {result['output'].get('primary_mood', 'N/A')}")
        return {"expert_outputs": [result]}
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return {"error": str(e), "expert_outputs": []}


def node_fusion(state: GraphState) -> Dict[str, Any]:
    """融合节点"""
    print(f"\n🔮 [FusionAgent] 融合专家输出...")

    # 如果是澄清模式，跳过融合
    if state.get("mode") == "clarification":
        print(f"   ⏭️  澄清模式，跳过融合")
        return {"fused_intent": None}

    session_id = state.get("session_id", "default")
    memory = get_or_create_memory(session_id)

    # 增量更新模式
    if state.get("mode") == "incremental":
        print(f"   📈 增量更新模式")
        last_intent = memory.get_last_intent()
        if last_intent:
            new_intent = memory.apply_incremental_update(state["user_input"], last_intent)
            print(f"   ✅ 应用增量更新: intensity={new_intent.style.intensity}, genre={new_intent.style.genre}")
            return {"fused_intent": new_intent}
        else:
            print(f"   ⚠️  无历史记录，回退到正常模式")

    # 正常融合模式
    print(f"   收到 {len(state.get('expert_outputs', []))} 个专家输出")

    try:
        intent = fusion_agent.fuse(state["user_input"], state.get("expert_outputs", []))
        print(f"   ✅ 完成: mode={intent.mode.value}, subject={intent.subject.entity}")
        return {"fused_intent": intent}
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def node_selector(state: GraphState) -> Dict[str, Any]:
    """选择节点"""
    # 如果是澄清模式或无融合意图，跳过
    if state.get("mode") == "clarification" or not state.get("fused_intent"):
        print(f"\n🎯 [SelectorAgent] 澄清模式，跳过选择")
        return {"selected_model": None}

    print(f"\n🎯 [SelectorAgent] 选择生成模型...")

    try:
        result = selector.select(state["fused_intent"])
        print(f"   ✅ 选择: {result['model_name']}")
        return {"selected_model": result["selected_model"]}
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return {"error": str(e)}


def node_prompt_engineer(state: GraphState) -> Dict[str, Any]:
    """提示词工程师节点"""
    # 如果是澄清模式或无融合意图，跳过
    if state.get("mode") == "clarification" or not state.get("fused_intent"):
        print(f"\n✍️  [PromptEngineer] 澄清模式，跳过")
        return {"final_prompt": None, "prompt_meta": None}

    print(f"\n✍️  [PromptEngineer] 设计专业提示词...")

    try:
        result = prompt_engineer.design(state["fused_intent"])
        prompt = result["prompt"]
        meta = result["meta"]

        print(f"   ✅ 完成")
        print(f"   📷 摄影: {meta.photo.focal_length or 'N/A'}, {meta.photo.aperture or 'N/A'}")
        print(f"   💡 光影: {meta.lighting.direction or 'N/A'}")
        print(f"   🎨 色彩: {meta.color.dominant_hue or 'N/A'}")
        print(f"   📝 提示词: {prompt[:80]}...")

        return {
            "final_prompt": prompt,
            "prompt_meta": {
                "photo": {
                    "focal_length": meta.photo.focal_length,
                    "aperture": meta.photo.aperture,
                    "color_temperature": meta.photo.color_temperature,
                    "film_grain": meta.photo.film_grain
                },
                "lighting": {
                    "direction": meta.lighting.direction,
                    "quality": meta.lighting.quality,
                    "atmosphere": meta.lighting.atmosphere
                },
                "composition": {
                    "shot_size": meta.composition.shot_size,
                    "angle": meta.composition.angle,
                    "rule": meta.composition.rule
                },
                "color": {
                    "dominant_hue": meta.color.dominant_hue,
                    "complementary": meta.color.complementary,
                    "hex_codes": meta.color.hex_codes,
                    "film_stock": meta.color.film_stock
                },
                "narrative": meta.narrative
            }
        }
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def node_generator(state: GraphState) -> Dict[str, Any]:
    """生成节点"""
    # 如果是澄清模式或无融合意图，跳过生成
    if state.get("mode") == "clarification" or not state.get("fused_intent"):
        print(f"\n🖼️  [GeneratorAgent] 澄清模式，跳过生成")
        return {"final_output": None}

    if not state.get("selected_model"):
        return {"error": "未选择生成模型"}

    if not state.get("final_prompt"):
        return {"error": "未生成提示词"}

    print(f"\n🖼️  [GeneratorAgent] 生成图像...")

    try:
        intent = state["fused_intent"]
        image_url = generator.generate(
            prompt=state["final_prompt"],
            model=state["selected_model"],
            aspect_ratio=intent.output.aspect_ratio
        )
        print(f"   ✅ 完成:")
        print(f"      {image_url}")

        # 保存到会话记忆
        session_id = state.get("session_id", "default")
        memory = get_or_create_memory(session_id)
        memory.add_record(
            user_input=state["user_input"],
            intent=intent,
            image_url=image_url
        )
        print(f"   💾 已保存到会话记忆")

        return {"final_output": image_url}
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# 构建图 - 添加条件边
def create_workflow():
    workflow = StateGraph(GraphState)

    # 添加节点
    workflow.add_node("scheduler", node_scheduler)
    workflow.add_node("vision_expert", node_vision)
    workflow.add_node("style_expert", node_style)
    workflow.add_node("mood_expert", node_mood)
    workflow.add_node("fusion", node_fusion)
    workflow.add_node("selector", node_selector)
    workflow.add_node("prompt_engineer", node_prompt_engineer)  # ← 新增
    workflow.add_node("generator", node_generator)

    # 添加边
    workflow.set_entry_point("scheduler")

    # 从 scheduler 分发到各专家（并行）
    workflow.add_edge("scheduler", "vision_expert")
    workflow.add_edge("scheduler", "style_expert")
    workflow.add_edge("scheduler", "mood_expert")

    # 专家汇聚到 fusion
    workflow.add_edge("vision_expert", "fusion")
    workflow.add_edge("style_expert", "fusion")
    workflow.add_edge("mood_expert", "fusion")

    # fusion 后条件分支
    def after_fusion(state: GraphState) -> str:
        if state.get("mode") == "clarification":
            return "end"
        return "continue"

    workflow.add_conditional_edges(
        "fusion",
        after_fusion,
        {
            "continue": "selector",
            "end": END
        }
    )

    # selector → prompt_engineer → generator
    workflow.add_edge("selector", "prompt_engineer")   # ← 新增
    workflow.add_edge("prompt_engineer", "generator")  # ← 新增
    workflow.add_edge("generator", END)

    return workflow.compile()


# 全局编译
app = create_workflow()