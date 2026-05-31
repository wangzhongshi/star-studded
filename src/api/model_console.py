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
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..services.model_manager import ModelManager
from ..services.model_validator import ModelValidator

router = APIRouter(prefix="/api/v1/models", tags=["模型调度台"])


# ============ 请求/响应模型 ============

class ModelCreateRequest(BaseModel):
    model_key: str = Field(..., description="模型唯一标识", example="flux-dev")
    model_name: str = Field(..., description="显示名称", example="Flux Dev")
    provider: str = Field(..., description="厂商", example="blackforestlabs")
    api_type: str = Field(default="openai", description="API类型: openai/aliyun/volces/custom")
    api_key: str = Field(..., description="API Key")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    model_id: str = Field(..., description="厂商侧模型ID", example="flux-dev")
    capabilities: List[str] = Field(default=["image"], description="能力标签")
    strengths: List[str] = Field(default=[], description="擅长领域")
    params: dict = Field(default={}, description="模型参数")
    prompt_template: Optional[str] = Field(default=None, description="提示词模板")


class ModelUpdateRequest(BaseModel):
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    capabilities: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    params: Optional[dict] = None
    prompt_template: Optional[str] = None
    is_active: Optional[int] = None


class ModelResponse(BaseModel):
    id: int
    model_key: str
    model_name: str
    provider: str
    api_type: str
    base_url: Optional[str]
    model_id: str
    capabilities_json: List[str]
    strengths_json: Optional[List[str]]
    is_active: int
    is_verified: int
    is_builtin: int
    call_count: int
    error_count: int


class ValidateResponse(BaseModel):
    success: bool
    message: str
    latency_ms: int


# ============ API 路由 ============

@router.get("/", response_model=List[ModelResponse])
def list_models(active_only: bool = True, db: Session = Depends(get_db)):
    """列出所有模型"""
    manager = ModelManager(db)
    models = manager.list_models(active_only=active_only)
    return models


@router.get("/{model_key}", response_model=ModelResponse)
def get_model(model_key: str, db: Session = Depends(get_db)):
    """获取单个模型"""
    manager = ModelManager(db)
    model = manager.get_model(model_key)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return model


@router.post("/", response_model=ModelResponse)
def add_model(request: ModelCreateRequest, db: Session = Depends(get_db)):
    """添加模型"""
    manager = ModelManager(db)

    # 检查是否已存在
    if manager.get_model(request.model_key):
        raise HTTPException(status_code=400, detail="模型标识已存在")

    data = request.dict()
    model = manager.add_model(data)
    return model


@router.put("/{model_key}", response_model=ModelResponse)
def update_model(model_key: str, request: ModelUpdateRequest, db: Session = Depends(get_db)):
    """更新模型"""
    manager = ModelManager(db)
    model = manager.update_model(model_key, request.dict(exclude_unset=True))
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在或无法修改内置模型")
    return model


@router.delete("/{model_key}")
def delete_model(model_key: str, db: Session = Depends(get_db)):
    """删除模型（仅限用户添加的）"""
    manager = ModelManager(db)
    success = manager.delete_model(model_key)
    if not success:
        raise HTTPException(status_code=404, detail="模型不存在或无法删除内置模型")
    return {"message": "删除成功"}


@router.post("/{model_key}/validate", response_model=ValidateResponse)
def validate_model(model_key: str, db: Session = Depends(get_db)):
    """验证模型 API"""
    validator = ModelValidator(db)
    result = validator.validate(model_key)
    return result


@router.post("/{model_key}/activate")
def activate_model(model_key: str, db: Session = Depends(get_db)):
    """启用模型"""
    manager = ModelManager(db)
    model = manager.update_model(model_key, {"is_active": 1})
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return {"message": "已启用"}


@router.post("/{model_key}/deactivate")
def deactivate_model(model_key: str, db: Session = Depends(get_db)):
    """禁用模型"""
    manager = ModelManager(db)
    model = manager.update_model(model_key, {"is_active": 0})
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return {"message": "已禁用"}