import os
import sys
import tempfile
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from graph.workflow import app as workflow_app, GraphState, get_or_create_memory

app = FastAPI(
    title="众星云集 - 人味",
    description="多智能体AI图像创作平台 - 支持会话记忆和主动交互",
    version="0.3.0"
)


@app.post("/generate")
async def generate_image(
        message: str = Form(..., description="用户描述"),
        image: UploadFile = File(None, description="参考图片"),
        session_id: str = Form("default", description="会话ID")
):
    """
    主生成接口
    - 支持纯文本、带图片、增量更新
    - 意图模糊时主动追问
    """
    try:
        # 处理上传的图片
        image_path = None
        if image:
            suffix = os.path.splitext(image.filename)[1] or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await image.read()
                tmp.write(content)
                image_path = tmp.name

        # 构建初始状态
        user_input = f"[图片路径: {image_path}] {message}" if image_path else message

        initial_state: GraphState = {
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

        # 调用工作流
        result = workflow_app.invoke(initial_state)

        # 清理临时文件
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)

        # 检查是否需要追问
        if result.get("mode") == "clarification":
            return JSONResponse({
                "success": True,
                "needs_clarification": True,
                "questions": result.get("questions", []),
                "message": "我需要更多信息才能创作",
                "session_id": session_id
            })

        # 检查错误
        if result.get("error"):
            return JSONResponse({
                "success": False,
                "error": result["error"],
                "session_id": session_id
            }, status_code=500)

        # 正常返回
        return JSONResponse({
            "success": True,
            "image_url": result.get("final_output"),
            "intent": result["fused_intent"].to_dict() if result.get("fused_intent") else None,
            "session_id": session_id,
            "mode": result.get("mode", "normal")
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


@app.post("/feedback")
async def submit_feedback(
        session_id: str = Form(...),
        feedback: str = Form(...),  # "good", "bad", "modify"
        message: Optional[str] = Form(None)
):
    """
    提交反馈，用于迭代优化
    """
    try:
        memory = get_or_create_memory(session_id)

        if memory.history:
            memory.history[-1].feedback = feedback
            print(f"💾 会话 {session_id} 反馈已记录: {feedback}")

        return JSONResponse({
            "success": True,
            "message": "反馈已记录",
            "session_id": session_id
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


@app.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """
    获取会话历史
    """
    try:
        memory = get_or_create_memory(session_id)

        history = []
        for record in memory.history:
            history.append({
                "timestamp": record.timestamp,
                "user_input": record.user_input,
                "intent": record.intent.to_dict(),
                "image_url": record.image_url,
                "feedback": record.feedback
            })

        return JSONResponse({
            "success": True,
            "session_id": session_id,
            "history_count": len(history),
            "history": history
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "0.3.0", "features": ["session_memory", "clarification"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)