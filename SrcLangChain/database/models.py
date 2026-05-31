from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql import func
from .connection import Base


class ModelRegistry(Base):
    """模型注册表"""
    __tablename__ = "model_registry"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_key = Column(String(64), nullable=False, unique=True, comment="模型唯一标识")
    model_name = Column(String(128), nullable=False, comment="显示名称")
    provider = Column(String(64), nullable=False, comment="厂商")
    api_type = Column(String(32), nullable=False, default="openai", comment="API类型")
    api_key_encrypted = Column(String(512), nullable=True, comment="加密后的API Key")
    base_url = Column(String(256), nullable=True, comment="API基础URL")
    model_id = Column(String(128), nullable=False, comment="模型ID（厂商侧标识）")
    capabilities_json = Column(JSON, nullable=False, comment="能力标签")
    strengths_json = Column(JSON, nullable=True, comment="擅长领域")
    params_json = Column(JSON, nullable=True, comment="模型参数")
    prompt_template = Column(Text, nullable=True, comment="提示词模板")
    is_active = Column(TINYINT, nullable=False, default=1, comment="0-禁用 1-启用")
    is_verified = Column(TINYINT, nullable=False, default=0, comment="0-未验证 1-已验证")
    verified_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    call_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    is_builtin = Column(TINYINT, nullable=False, default=0, comment="0-用户添加 1-系统内置")
    user_id = Column(BigInteger, nullable=True, comment="添加者ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class ModelCallLog(Base):
    """模型调用日志"""
    __tablename__ = "model_call_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_id = Column(BigInteger, nullable=False, comment="关联model_registry.id")
    creation_record_id = Column(BigInteger, nullable=True, comment="关联creation_record.id")
    request_type = Column(String(32), nullable=False, comment="请求类型")
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)
    status = Column(TINYINT, nullable=False, default=1, comment="0-失败 1-成功")
    error_msg = Column(String(512), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class CreationRecord(Base):
    """创作记录表"""
    __tablename__ = "creation_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    user_input = Column(String(512), nullable=False)
    mode = Column(String(32), nullable=False, default="normal")
    intent_json = Column(JSON, nullable=False)
    subject_entity = Column(String(128), nullable=True)
    style_genre = Column(String(64), nullable=True)
    expert_outputs_json = Column(JSON, nullable=True)
    scheduled_experts = Column(String(128), nullable=True)
    final_prompt = Column(Text, nullable=False)
    prompt_meta_json = Column(JSON, nullable=True)
    selected_model = Column(String(64), nullable=False)
    image_url = Column(String(512), nullable=True)
    video_url = Column(String(512), nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    user_rating = Column(TINYINT, nullable=True)
    user_feedback = Column(String(256), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())