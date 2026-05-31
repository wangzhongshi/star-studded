import time
from typing import Dict, Any, Optional
from openai import OpenAI

from ..database.models import ModelRegistry
from .model_manager import ModelManager


class ModelValidator:
    """
    模型验证器
    职责：验证用户提交的 API 是否可用
    """

    def __init__(self, db):
        self.db = db
        self.manager = ModelManager(db)

    def validate(self, model_key: str) -> Dict[str, Any]:
        """
        验证模型 API 是否可用
        返回: {"success": bool, "message": str, "latency_ms": int}
        """
        model = self.manager.get_model(model_key)
        if not model:
            return {"success": False, "message": "模型不存在", "latency_ms": 0}

        # 获取解密后的 API Key
        api_key = self.manager.get_model_api_key(model_key)
        if not api_key:
            return {"success": False, "message": "API Key 未配置", "latency_ms": 0}

        start_time = time.time()

        try:
            # 根据 api_type 创建客户端
            if model.api_type == "openai":
                client = OpenAI(api_key=api_key, base_url=model.base_url)
            elif model.api_type == "aliyun":
                # 阿里云百炼兼容 OpenAI 格式
                client = OpenAI(api_key=api_key, base_url=model.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1")
            elif model.api_type == "volces":
                # 火山引擎
                client = OpenAI(api_key=api_key, base_url=model.base_url or "https://ark.cn-beijing.volces.com/api/v3")
            else:
                return {"success": False, "message": f"不支持的 API 类型: {model.api_type}", "latency_ms": 0}

            # 发送测试请求
            if "image" in model.capabilities_json or "video" in model.capabilities_json:
                # 图像/视频生成模型：发 images.generate 测试
                result = self._test_image_model(client, model)
            else:
                # LLM 模型：发 chat.completions 测试
                result = self._test_llm_model(client, model)

            latency_ms = int((time.time() - start_time) * 1000)

            # 记录日志
            self.manager.record_call(
                model_id=model.id,
                request_type="validate",
                status=1 if result["success"] else 0,
                latency_ms=latency_ms,
                error_msg=result.get("message") if not result["success"] else None
            )

            # 如果成功，标记为已验证
            if result["success"]:
                self.manager.verify_model(model_key)

            return {
                "success": result["success"],
                "message": result["message"],
                "latency_ms": latency_ms
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            self.manager.record_call(
                model_id=model.id,
                request_type="validate",
                status=0,
                latency_ms=latency_ms,
                error_msg=str(e)
            )
            return {
                "success": False,
                "message": f"验证异常: {str(e)}",
                "latency_ms": latency_ms
            }

    def _test_llm_model(self, client, model: ModelRegistry) -> Dict[str, Any]:
        """测试 LLM 模型"""
        try:
            response = client.chat.completions.create(
                model=model.model_id,
                messages=[{"role": "user", "content": "你好，请返回JSON格式: {\"status\": \"ok\"}"}],
                max_tokens=50,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            if content and "ok" in content:
                return {"success": True, "message": "LLM 测试通过"}
            return {"success": False, "message": f"返回内容异常: {content}"}
        except Exception as e:
            return {"success": False, "message": f"LLM 测试失败: {str(e)}"}

    def _test_image_model(self, client, model: ModelRegistry) -> Dict[str, Any]:
        """测试图像生成模型"""
        try:
            response = client.images.generate(
                model=model.model_id,
                prompt="test, a simple red circle, minimal",
                size="1024x1024",
                n=1
            )
            if response.data and response.data[0].url:
                return {"success": True, "message": "图像生成测试通过"}
            return {"success": False, "message": "未返回图像 URL"}
        except Exception as e:
            # 有些模型可能不支持测试生成，降级为 LLM 测试
            if "billing" in str(e).lower() or "quota" in str(e).lower():
                return {"success": False, "message": f"额度不足: {str(e)}"}
            return {"success": False, "message": f"图像测试失败: {str(e)}"}