from typing import List, Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database.models import ModelRegistry, ModelCallLog
from ..utils.crypto import crypto


class ModelManager:
    """
    模型管理器
    职责：CRUD + 加密 + 查询
    """

    def __init__(self, db: Session):
        self.db = db

    def list_models(self, active_only: bool = True, user_id: Optional[int] = None) -> List[ModelRegistry]:
        """列出模型"""
        query = self.db.query(ModelRegistry)
        if active_only:
            query = query.filter(ModelRegistry.is_active == 1)
        if user_id:
            query = query.filter(
                (ModelRegistry.user_id == user_id) | (ModelRegistry.is_builtin == 1)
            )
        return query.all()

    def get_model(self, model_key: str) -> Optional[ModelRegistry]:
        """获取单个模型"""
        return self.db.query(ModelRegistry).filter(ModelRegistry.model_key == model_key).first()

    def add_model(self, data: Dict[str, Any], user_id: Optional[int] = None) -> ModelRegistry:
        """
        添加模型
        """
        # 加密 API Key
        api_key = data.get("api_key")
        encrypted_key = crypto.encrypt(api_key) if api_key else None

        model = ModelRegistry(
            model_key=data["model_key"],
            model_name=data["model_name"],
            provider=data["provider"],
            api_type=data.get("api_type", "openai"),
            api_key_encrypted=encrypted_key,
            base_url=data.get("base_url"),
            model_id=data["model_id"],
            capabilities_json=data.get("capabilities", []),
            strengths_json=data.get("strengths", []),
            params_json=data.get("params", {}),
            prompt_template=data.get("prompt_template"),
            is_active=1,
            is_verified=0,
            is_builtin=0,
            user_id=user_id
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def update_model(self, model_key: str, data: Dict[str, Any]) -> Optional[ModelRegistry]:
        """更新模型"""
        model = self.get_model(model_key)
        if not model:
            return None

        # 更新字段
        for field in ["model_name", "provider", "api_type", "base_url",
                      "model_id", "capabilities_json", "strengths_json",
                      "params_json", "prompt_template", "is_active"]:
            if field in data:
                setattr(model, field, data[field])

        # API Key 单独处理（加密）
        if "api_key" in data:
            model.api_key_encrypted = crypto.encrypt(data["api_key"])

        self.db.commit()
        self.db.refresh(model)
        return model

    def delete_model(self, model_key: str) -> bool:
        """删除模型（仅限用户添加的）"""
        model = self.get_model(model_key)
        if not model or model.is_builtin:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    def verify_model(self, model_key: str) -> bool:
        """标记模型为已验证"""
        model = self.get_model(model_key)
        if not model:
            return False

        model.is_verified = 1
        model.verified_at = func.now()
        self.db.commit()
        return True

    def record_call(self, model_id: int, request_type: str,
                    status: int, latency_ms: Optional[int] = None,
                    error_msg: Optional[str] = None,
                    request_payload: Optional[Dict] = None,
                    response_payload: Optional[Dict] = None,
                    creation_record_id: Optional[int] = None):
        """记录调用日志"""
        log = ModelCallLog(
            model_id=model_id,
            creation_record_id=creation_record_id,
            request_type=request_type,
            request_payload=request_payload,
            response_payload=response_payload,
            status=status,
            error_msg=error_msg,
            latency_ms=latency_ms
        )
        self.db.add(log)
        self.db.commit()

    def get_model_api_key(self, model_key: str) -> Optional[str]:
        """获取解密后的 API Key"""
        model = self.get_model(model_key)
        if not model or not model.api_key_encrypted:
            return None
        return crypto.decrypt(model.api_key_encrypted)