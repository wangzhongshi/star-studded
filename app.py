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

os.environ["DEEPSEEK_API_KEY"] = "your-api-key"
os.environ["DASHSCOPE_API_KEY"] = "your-api-key"
os.environ["ARK_API_KEY"] = "your-api-key"
import sys
import json
import time
import uuid
from flask import Flask, request, Response, jsonify, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.graph.workflow import app as workflow_app, get_or_create_memory


app = Flask(__name__, static_folder='static')
CORS(app)


# ============ 文件上传配置 ============
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============ 星星角色配置 ============
STAR_CHARACTERS = {
    "scheduler": {
        "name": "小调",
        "emoji": "⭐",
        "color": "#FFB800",
        "personality": "热情活泼的组织者",
        "speak_style": "元气满满"
    },
    "vision": {
        "name": "小视",
        "emoji": "👁️",
        "color": "#00D4FF",
        "personality": "敏锐细致的观察家",
        "speak_style": "冷静分析"
    },
    "style": {
        "name": "小风",
        "emoji": "🎨",
        "color": "#FF6B9D",
        "personality": "文艺有品味的艺术家",
        "speak_style": "优雅诗意"
    },
    "mood": {
        "name": "小情",
        "emoji": "💭",
        "color": "#9B59B6",
        "personality": "温柔敏感的心灵捕手",
        "speak_style": "温暖共情"
    },
    "fusion": {
        "name": "小融",
        "emoji": "🔮",
        "color": "#E74C3C",
        "personality": "智慧统筹的融合大师",
        "speak_style": "沉稳睿智"
    },
    "selector": {
        "name": "小选",
        "emoji": "🎯",
        "color": "#2ECC71",
        "personality": "果断专业的决策者",
        "speak_style": "干脆利落"
    },
    "prompt_engineer": {
        "name": "小词",
        "emoji": "✍️",
        "color": "#3498DB",
        "personality": "严谨专业的技术控",
        "speak_style": "精确细致"
    },
    "auditor": {
        "name": "小审",
        "emoji": "🔍",
        "color": "#E67E22",
        "personality": "严肃正义的守护者",
        "speak_style": "认真刻板"
    },
    "generator": {
        "name": "小画",
        "emoji": "🖼️",
        "color": "#1ABC9C",
        "personality": "富有创造力的画家",
        "speak_style": "艺术感性"
    }
}


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


def generate_star_message(step_id: str, context: dict) -> dict:
    """根据步骤生成星星的拟人化说话内容"""
    star = STAR_CHARACTERS.get(step_id, STAR_CHARACTERS["scheduler"])

    messages = {
        "scheduler": [
            "收到收到！让我先看看你想要什么～",
            "来啦来啦！小调正在分析你的需求...",
            "嗯嗯，让我理解一下你的想法 ✨"
        ],
        "vision": [
            "让我仔细看看这张图...",
            "小视正在观察画面细节 👀",
            "图像里有很多有趣的信息呢..."
        ],
        "style": [
            "这个风格很有品味，让我想想...",
            "小风感受到了艺术的气息 🎨",
            "让我找找最适合的流派..."
        ],
        "mood": [
            "我感受到了情绪的温度...",
            "小情正在捕捉氛围 💭",
            "这种感觉很特别呢..."
        ],
        "fusion": [
            "让我把大家的想法融合在一起...",
            "小融正在统筹全局 🔮",
            "各种灵感正在汇聚..."
        ],
        "selector": [
            "让我选个最合适的模型...",
            "小选正在评估各个选项 🎯",
            "这个任务交给谁最好呢..."
        ],
        "prompt_engineer": [
            "现在开始设计专业提示词...",
            "小词正在精心打磨每个细节 ✍️",
            "让我把想法变成精确的语言..."
        ],
        "auditor": [
            "让我检查一下是否合规...",
            "小审正在认真审查 🔍",
            "安全第一，让我把关..."
        ],
        "generator": [
            "画笔准备好啦！开始创作...",
            "小画正在施展魔法 🖼️",
            "想象正在变成现实..."
        ]
    }

    import random
    texts = messages.get(step_id, ["正在努力工作中..."])
    text = random.choice(texts)

    if step_id == "scheduler" and context.get("mode") == "clarification":
        text = "嗯...你的描述有点抽象呢，能让我多了解一点吗？🤔"
    elif step_id == "scheduler" and context.get("experts"):
        text = f"好的！我请来了 {len(context['experts'])} 位专家帮忙 ✨"
    elif step_id == "fusion" and context.get("subject"):
        text = f"融合完成！主题是「{context['subject']}」🎉"
    elif step_id == "selector" and context.get("model"):
        text = f"决定啦！让 {context['model']} 来创作 🎯"
    elif step_id == "generator" and context.get("success"):
        text = "画好啦！快看看满意吗？🎨"

    return {
        "star_id": step_id,
        "star_name": star["name"],
        "emoji": star["emoji"],
        "color": star["color"],
        "personality": star["personality"],
        "message": text,
        "mood": "working"
    }


def stream_workflow(user_input: str, session_id: str, image_path: str = None):
    """流式执行 workflow，对话式 SSE 事件"""
    state = create_initial_state(user_input, session_id)
    if image_path:
        state["image_path"] = image_path
        state["has_image"] = True

    def send_event(event_type: str, data: dict):
        event = {"type": event_type, **data, "timestamp": time.time()}
        return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    def send_user_message(text: str):
        return send_event("user_message", {"text": text})

    def send_star_speak(star_data: dict, is_typing: bool = True):
        return send_event("star_speak", {**star_data, "is_typing": is_typing})

    def send_progress(current: int, total: int, message: str):
        return send_event("progress", {
            "current": current, "total": total,
            "percentage": int(current / total * 100), "message": message
        })

    def send_result(image_url: str = None, error: str = None, questions: list = None,
                    prompt: str = None, meta: dict = None, mode: str = None,
                    clarification_round: int = 0, max_rounds: int = 6):
        return send_event("result", {
            "image_url": image_url, "error": error, "questions": questions,
            "prompt": prompt, "meta": meta, "mode": mode,
            "clarification_round": clarification_round,
            "max_clarification_rounds": max_rounds,
            "remaining_rounds": max_rounds - clarification_round
        })

    # 先显示用户消息
    yield send_user_message(user_input)

    try:
        # 先告诉用户我们正在开始
        yield send_star_speak({
            "star_id": "scheduler", "star_name": "小调", "emoji": "⭐",
            "color": "#FFB800", "personality": "热情活泼的组织者",
            "message": "收到！让我召集星星们开始创作 ✨", "mood": "happy"
        }, is_typing=False)

        # 显示工作中状态
        yield send_star_speak({
            "star_id": "scheduler", "star_name": "小调", "emoji": "⭐",
            "color": "#FFB800", "personality": "热情活泼的组织者",
            "message": "星星们正在努力工作中...", "mood": "working"
        }, is_typing=True)

        # 执行 workflow（这可能需要几秒）
        result = workflow_app.invoke(state)

        # invoke 完成后，根据结果展示各星星
        # ===== Step 1: Scheduler =====
        if result.get("mode") == "clarification":
            memory = get_or_create_memory(session_id)
            questions = result.get("questions") or memory.generate_follow_up_questions(user_input)
            current_round = result.get("clarification_round", memory.clarification_rounds)
            max_rounds = result.get("max_clarification_rounds", memory.max_clarification_rounds)

            yield send_star_speak({
                "star_id": "scheduler", "star_name": "小调", "emoji": "⭐",
                "color": "#FFB800", "personality": "热情活泼的组织者",
                "message": f"我还需要多了解一点～能告诉我：{questions[0] if questions else '更多细节吗？'}",
                "mood": "thinking"
            }, is_typing=False)

            yield send_progress(1, 7, "需要澄清")
            yield send_result(
                questions=questions, mode="clarification",
                clarification_round=current_round, max_rounds=max_rounds
            )
            return

        experts = result.get("scheduled_experts", [])
        yield send_star_speak(generate_star_message("scheduler", {
            "mode": "normal", "experts": experts
        }), is_typing=False)
        yield send_progress(1, 7, "需求分析完成")
        time.sleep(0.3)

        # ===== Step 2: Experts =====
        if "vision" in experts:
            yield send_star_speak(generate_star_message("vision", {}))
            time.sleep(0.6)
        if "style" in experts:
            yield send_star_speak(generate_star_message("style", {}))
            time.sleep(0.6)
        if "mood" in experts:
            yield send_star_speak(generate_star_message("mood", {}))
            time.sleep(0.6)

        yield send_star_speak({
            "star_id": "experts", "star_name": "专家们", "emoji": "✨",
            "color": "#888", "personality": "各司其职的专家团队",
            "message": "我们都分析完啦！交给小融来整合吧～", "mood": "happy"
        }, is_typing=False)
        yield send_progress(2, 7, "专家分析完成")
        time.sleep(0.3)

        # ===== Step 3: Fusion =====
        yield send_star_speak(generate_star_message("fusion", {}))
        time.sleep(0.5)
        intent = result.get("fused_intent")
        yield send_star_speak(generate_star_message("fusion", {
            "subject": intent.subject.entity if intent else ""
        }), is_typing=False)
        yield send_progress(3, 7, "意图融合完成")
        time.sleep(0.3)

        # ===== Step 4: Selector =====
        yield send_star_speak(generate_star_message("selector", {}))
        time.sleep(0.5)
        model = result.get("selected_model", "未知")
        yield send_star_speak(generate_star_message("selector", {"model": model}), is_typing=False)
        yield send_progress(4, 7, "模型选择完成")
        time.sleep(0.3)

        # ===== Step 5: PromptEngineer =====
        yield send_star_speak(generate_star_message("prompt_engineer", {}))
        time.sleep(0.8)
        final_prompt = result.get("final_prompt", "")
        yield send_star_speak({
            "star_id": "prompt_engineer", "star_name": "小词", "emoji": "✍️",
            "color": "#3498DB", "personality": "严谨专业的技术控",
            "message": f"提示词设计完成！用了 {len(final_prompt)} 个字符精心打磨 ✨", "mood": "happy"
        }, is_typing=False)
        yield send_progress(5, 7, "提示词设计完成")
        time.sleep(0.3)

        # ===== Step 6: Auditor =====
        yield send_star_speak(generate_star_message("auditor", {}))
        time.sleep(0.5)
        audit = result.get("audit_result", {})
        if audit and not audit.get("passed", True):
            yield send_star_speak({
                "star_id": "auditor", "star_name": "小审", "emoji": "🔍",
                "color": "#E67E22", "personality": "严肃正义的守护者",
                "message": f"审查未通过：{audit.get('message', '内容不合规')} 😤", "mood": "angry"
            }, is_typing=False)
            yield send_progress(6, 7, "审查未通过")
            yield send_result(error=f"提示词审查未通过: {audit.get('message', '')}")
            return

        yield send_star_speak({
            "star_id": "auditor", "star_name": "小审", "emoji": "🔍",
            "color": "#E67E22", "personality": "严肃正义的守护者",
            "message": "审查通过！内容很安全 ✅", "mood": "happy"
        }, is_typing=False)
        yield send_progress(6, 7, "安全审查通过")
        time.sleep(0.3)

        # ===== Step 7: Generator =====
        yield send_star_speak(generate_star_message("generator", {}))
        time.sleep(0.5)

        if result.get("final_output"):
            yield send_star_speak({
                "star_id": "generator", "star_name": "小画", "emoji": "🖼️",
                "color": "#1ABC9C", "personality": "富有创造力的画家",
                "message": "画好啦！快看看满意吗？🎨✨", "mood": "excited"
            }, is_typing=False)
            yield send_progress(7, 7, "完成！")

            prompt_meta = result.get("prompt_meta", {})
            yield send_result(
                image_url=result["final_output"], prompt=final_prompt,
                meta=prompt_meta, mode="normal"
            )
        else:
            yield send_star_speak({
                "star_id": "generator", "star_name": "小画", "emoji": "🖼️",
                "color": "#1ABC9C", "personality": "富有创造力的画家",
                "message": "哎呀，生成出了点问题... 😢", "mood": "sad"
            }, is_typing=False)
            yield send_result(error=result.get("error", "未知错误"))

    except Exception as e:
        yield send_star_speak({
            "star_id": "system", "star_name": "系统", "emoji": "⚠️",
            "color": "#FF4444", "personality": "系统提示",
            "message": f"出错了：{str(e)}", "mood": "sad"
        }, is_typing=False)
        yield send_result(error=str(e))


@app.route("/")
def index():
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(os.path.join(static_path, 'index.html')):
        return f"找不到 index.html，请确认文件在: {static_path}", 404
    return send_from_directory(static_path, 'index.html')


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    user_input = data.get("user_input", "")
    session_id = data.get("session_id", "default")
    image_path = data.get("image_path")

    if not user_input:
        return jsonify({"error": "请输入描述"}), 400

    return Response(
        stream_workflow(user_input, session_id, image_path),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@app.route("/api/upload", methods=["POST"])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "没有文件"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        return jsonify({
            "success": True,
            "image_path": filepath,
            "filename": filename
        })

    return jsonify({"error": "不支持的文件类型"}), 400


@app.route("/api/models", methods=["GET"])
def list_models():
    from src.database.connection import SessionLocal
    from src.services.model_manager import ModelManager

    db = SessionLocal()
    try:
        manager = ModelManager(db)
        models = manager.list_models(active_only=True)
        return jsonify([{
            "model_key": m.model_key, "model_name": m.model_name,
            "provider": m.provider, "capabilities": m.capabilities_json,
            "is_verified": m.is_verified
        } for m in models])
    finally:
        db.close()


@app.route("/api/models/validate", methods=["POST"])
def validate_model():
    data = request.json
    model_key = data.get("model_key")

    from src.database.connection import SessionLocal
    from src.services.model_validator import ModelValidator

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