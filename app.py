import os
os.environ["DEEPSEEK_API_KEY"] = "your-api-key"
os.environ["DASHSCOPE_API_KEY"] = "your-api-key"
os.environ["ARK_API_KEY"] = "your-api-key"
import sys
import json
import time
from flask import Flask, request, Response, jsonify, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from SrcLangChain.graph.workflow import app as workflow_app, get_or_create_memory
from SrcLangChain.services.prompt_auditor import auditor


app = Flask(__name__, static_folder='static')
CORS(app)


def create_initial_state(user_input: str, session_id: str = "default"):
    return {
        "user_input": user_input,
        "session_id": session_id,
        "image_path": None,
        "has_image": False,
        "scheduled_experts": [],
        "expert_outputs": [],
        "fused_intent": None,
        "selected_model": None,
        "final_prompt": None,
        "prompt_meta": None,
        "audit_result": None,
        "final_output": None,
        "error": None,
        "mode": None,
        "questions": None
    }


def stream_workflow(user_input: str, session_id: str):
    """
    流式执行 workflow，每完成一步发送 SSE 事件
    """
    state = create_initial_state(user_input, session_id)

    steps = [
        {"id": "scheduler", "name": "🔀 分析需求", "status": "pending"},
        {"id": "experts", "name": "👁️ 专家分析", "status": "pending"},
        {"id": "fusion", "name": "🔮 融合意图", "status": "pending"},
        {"id": "selector", "name": "🎯 选择模型", "status": "pending"},
        {"id": "prompt_engineer", "name": "✍️ 设计提示词", "status": "pending"},
        {"id": "auditor", "name": "🔍 安全审查", "status": "pending"},
        {"id": "generator", "name": "🖼️ 生成图像", "status": "pending"},
    ]

    def send_event(event_type: str, data: dict):
        event = {
            "type": event_type,
            **data,
            "timestamp": time.time()
        }
        return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    def send_step(step_id: str, status: str, detail: str = "", extra: dict = None):
        return send_event("step", {
            "step_id": step_id,
            "status": status,
            "detail": detail,
            "data": extra or {}
        })

    def send_progress(current: int, total: int, message: str):
        return send_event("progress", {
            "current": current,
            "total": total,
            "percentage": int(current / total * 100),
            "message": message
        })

    def send_result(image_url: str = None, error: str = None, questions: list = None, prompt: str = None, meta: dict = None):
        return send_event("result", {
            "image_url": image_url,
            "error": error,
            "questions": questions,
            "prompt": prompt,
            "meta": meta
        })

    yield send_progress(0, 7, "开始分析...")

    try:
        # 执行完整 workflow
        result = workflow_app.invoke(state)

        # 根据结果反推各步骤状态（简化版）
        # Step 1: Scheduler
        yield send_step("scheduler", "running", "正在分析您的需求...")
        time.sleep(0.3)

        if result.get("mode") == "clarification":
            yield send_step("scheduler", "completed", "需要更多信息")
            memory = get_or_create_memory(session_id)
            questions = memory.generate_follow_up_questions(user_input)
            yield send_progress(1, 7, "需要澄清")
            yield send_result(questions=questions)
            return

        experts = result.get("scheduled_experts", [])
        yield send_step("scheduler", "completed", f"调度了 {len(experts)} 个专家", {
            "experts": experts,
            "mode": result.get("mode", "normal")
        })
        yield send_progress(1, 7, "需求分析完成")

        # Step 2: Experts
        yield send_step("experts", "running", "专家正在分析...")
        time.sleep(0.3)
        yield send_step("experts", "completed", "专家分析完成")
        yield send_progress(2, 7, "专家分析完成")

        # Step 3: Fusion
        yield send_step("fusion", "running", "融合专家输出...")
        time.sleep(0.3)
        intent = result.get("fused_intent")
        yield send_step("fusion", "completed", "意图融合完成", {
            "subject": intent.subject.entity if intent else "",
            "genre": intent.style.genre if intent else ""
        })
        yield send_progress(3, 7, "意图融合完成")

        # Step 4: Selector
        yield send_step("selector", "running", "选择最优模型...")
        time.sleep(0.3)
        yield send_step("selector", "completed", f"选择模型: {result.get('selected_model', 'N/A')}")
        yield send_progress(4, 7, "模型选择完成")

        # Step 5: PromptEngineer
        yield send_step("prompt_engineer", "running", "设计专业提示词...")
        time.sleep(0.3)
        final_prompt = result.get("final_prompt", "")
        prompt_meta = result.get("prompt_meta", {})
        yield send_step("prompt_engineer", "completed", "提示词设计完成", {
            "prompt_preview": final_prompt[:100] + "..." if len(final_prompt) > 100 else final_prompt,
            "photo": prompt_meta.get("photo", {}),
            "lighting": prompt_meta.get("lighting", {}),
            "composition": prompt_meta.get("composition", {}),
            "color": prompt_meta.get("color", {})
        })
        yield send_progress(5, 7, "提示词设计完成")

        # Step 6: Auditor
        yield send_step("auditor", "running", "安全审查中...")
        time.sleep(0.3)
        audit = result.get("audit_result", {})
        if audit and not audit.get("passed", True):
            yield send_step("auditor", "error", f"审查未通过: {audit.get('message', '')}")
            yield send_progress(6, 7, "审查未通过")
            yield send_result(error=f"提示词审查未通过: {audit.get('message', '')}")
            return
        yield send_step("auditor", "completed", "审查通过")
        yield send_progress(6, 7, "安全审查通过")

        # Step 7: Generator
        yield send_step("generator", "running", "正在生成图像...")
        if result.get("final_output"):
            yield send_step("generator", "completed", "图像生成完成")
            yield send_progress(7, 7, "完成！")
            yield send_result(
                image_url=result["final_output"],
                prompt=final_prompt,
                meta=prompt_meta
            )
        else:
            yield send_step("generator", "error", "生成失败")
            yield send_result(error=result.get("error", "未知错误"))

    except Exception as e:
        yield send_step("generator", "error", f"执行出错: {str(e)}")
        yield send_result(error=str(e))


@app.route("/")
def index():
    """首页"""
    return send_from_directory("SrcLangChain/static", "index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    """生成图像（流式）"""
    data = request.json
    user_input = data.get("user_input", "")
    session_id = data.get("session_id", "default")

    if not user_input:
        return jsonify({"error": "请输入描述"}), 400

    return Response(
        stream_workflow(user_input, session_id),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.route("/api/models", methods=["GET"])
def list_models():
    """列出可用模型"""
    from SrcLangChain.database.connection import SessionLocal
    from SrcLangChain.services.model_manager import ModelManager

    db = SessionLocal()
    try:
        manager = ModelManager(db)
        models = manager.list_models(active_only=True)
        return jsonify([{
            "model_key": m.model_key,
            "model_name": m.model_name,
            "provider": m.provider,
            "capabilities": m.capabilities_json,
            "is_verified": m.is_verified
        } for m in models])
    finally:
        db.close()


@app.route("/api/models/validate", methods=["POST"])
def validate_model():
    """验证模型"""
    data = request.json
    model_key = data.get("model_key")

    from SrcLangChain.database.connection import SessionLocal
    from SrcLangChain.services.model_validator import ModelValidator

    db = SessionLocal()
    try:
        validator = ModelValidator(db)
        result = validator.validate(model_key)
        return jsonify(result)
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 人味 AI 图像生成服务启动中...")
    print("📍 访问 http://localhost:5000")
    app.run(debug=True, port=5000, threaded=True)