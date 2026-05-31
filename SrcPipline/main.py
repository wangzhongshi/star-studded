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
import base64
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

from agents.intent_parser import IntentParser
from agents.vision_analyzer import VisionAnalyzer
from agents.adapters.seedream import SeedreamAdapter

app = FastAPI(title="众星云集 - 人味Demo", version="0.1.0")


@app.post("/generate")
async def generate_image(
        message: str = Form(...),
        image: UploadFile = File(None)
):
    """
    主流程：用户上传图片+说人话 → 出图
    """
    try:
        # 1. 处理上传的图片
        image_base64 = None
        if image:
            contents = await image.read()
            image_base64 = base64.b64encode(contents).decode("utf-8")

        # 2. 意图解析（DeepSeek）
        parser = IntentParser()
        intent = parser.parse(message, image_base64)

        # 3. 生成图像（Seedream）
        adapter = SeedreamAdapter()
        image_url = adapter.generate(intent)

        return JSONResponse({
            "success": True,
            "image_url": image_url,
            "intent": intent.to_dict(),
            "prompt_used": adapter.translate(intent)
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


@app.post("/chat")
async def chat_generate(
        message: str = Form(...),
        session_id: str = Form("default"),
        image: UploadFile = File(None)
):
    """
    对话式生成（支持迭代优化）
    """
    # TODO: 实现会话记忆和增量更新
    return await generate_image(message, image)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)