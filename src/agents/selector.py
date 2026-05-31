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
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..database.models import ModelRegistry
from ..services.model_manager import ModelManager


class SelectorAgent:
    """
    选择智能体（重构版）
    职责：基于模型注册表动态评分选择最优生成模型
    """

    def __init__(self, db: Session = None):
        self.db = db

    def select(self, intent: Any) -> Dict[str, Any]:
        """
        选择最优生成模型
        评分维度：能力匹配、质量需求、成本约束、速度约束、可用性
        """
        # 如果没有数据库连接，fallback 到硬编码
        if not self.db:
            return self._fallback_select(intent)

        manager = ModelManager(self.db)

        # 获取所有激活的图像生成模型
        models = manager.list_models(active_only=True)
        image_models = [m for m in models if "image" in (m.capabilities_json or [])]

        if not image_models:
            return self._fallback_select(intent)

        # 评分
        scored_models = []
        for model in image_models:
            score = self._score_model(model, intent)
            scored_models.append((model, score))

        # 排序选最高
        scored_models.sort(key=lambda x: x[1], reverse=True)
        best_model = scored_models[0][0]

        return {
            "selected_model": best_model.model_key,
            "model_name": best_model.model_name,
            "score": scored_models[0][1],
            "reasoning": f"选择 {best_model.model_name}（评分: {scored_models[0][1]}）"
        }

    def _score_model(self, model: ModelRegistry, intent: Any) -> float:
        """评分算法"""
        score = 0.0

        # 1. 可用性（是否验证通过）
        if model.is_verified:
            score += 30

        # 2. 能力匹配
        style_genre = intent.style.genre if hasattr(intent, 'style') else ""
        if style_genre and model.strengths_json:
            if any(s in style_genre for s in model.strengths_json):
                score += 25

        # 3. 中文支持
        if "chinese_prompt" in (model.capabilities_json or []):
            score += 20

        # 4. 速度
        if "fast" in (model.capabilities_json or []):
            score += 15

        # 5. 质量
        if "high_detail" in (model.capabilities_json or []):
            score += 10

        # 6. 调用成功率（错误率越低分越高）
        if model.call_count > 0:
            success_rate = 1 - (model.error_count / model.call_count)
            score += success_rate * 10

        return score

    def _fallback_select(self, intent: Any) -> Dict[str, Any]:
        """Fallback：硬编码选择 seedream"""
        return {
            "selected_model": "seedream",
            "model_name": "Doubao Seedream-5.0",
            "score": 0,
            "reasoning": "数据库未连接，fallback 到默认模型"
        }