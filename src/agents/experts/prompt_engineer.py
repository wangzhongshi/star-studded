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
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import os
import yaml

from ...models.intent import IntentRepresentation


@dataclass
class PhotoParams:
    """摄影参数"""
    focal_length: Optional[str] = None
    aperture: Optional[str] = None
    color_temperature: Optional[int] = None
    film_grain: Optional[str] = None


@dataclass
class LightingSetup:
    """光影设置"""
    direction: Optional[str] = None
    quality: Optional[str] = None
    key_light: Optional[str] = None
    fill_light: Optional[str] = None
    rim_light: Optional[str] = None
    atmosphere: Optional[str] = None


@dataclass
class CompositionRules:
    """构图法则"""
    shot_size: Optional[str] = None
    angle: Optional[str] = None
    rule: Optional[str] = None


@dataclass
class ColorScience:
    """色彩科学"""
    dominant_hue: Optional[str] = None
    complementary: Optional[str] = None
    hex_codes: Optional[List[str]] = None
    film_stock: Optional[str] = None


@dataclass
class PromptMeta:
    """提示词元数据（用于创作回放）"""
    photo: PhotoParams = field(default_factory=PhotoParams)
    lighting: LightingSetup = field(default_factory=LightingSetup)
    composition: CompositionRules = field(default_factory=CompositionRules)
    color: ColorScience = field(default_factory=ColorScience)
    narrative: str = ""
    raw_prompt: str = ""


class PromptEngineer:
    """
    提示词工程师智能体
    职责：将 IntentRepresentation 转化为模型专属的专业级提示词

    核心差异化：豆包需要用户自己写提示词 → 人味帮用户设计顶级提示词
    """

    def __init__(self):
        self.styles_config = self._load_styles_config()
        self.style_map = self.styles_config.get("styles", {})
        self.composition_map = self.styles_config.get("compositions", {})

    def _load_styles_config(self) -> Dict[str, Any]:
        """加载风格映射配置"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "config", "prompt_styles.yaml"
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"⚠️  未找到风格配置文件: {config_path}")
            return {}
        except Exception as e:
            print(f"⚠️  加载风格配置失败: {e}")
            return {}

    def design(self, intent: IntentRepresentation) -> Dict[str, Any]:
        """
        主入口：设计提示词
        返回: {
            "prompt": str,           # 最终提示词
            "meta": PromptMeta       # 元数据（创作回放用）
        }
        """
        # 1. 推断各项参数
        photo = self._infer_photo_params(intent)
        lighting = self._infer_lighting(intent)
        composition = self._infer_composition(intent)
        color = self._infer_color(intent)
        narrative = self._generate_narrative(intent)

        # 2. 拼接 Seedream 中文提示词
        prompt = self._build_seedream_prompt(
            intent, photo, lighting, composition, color, narrative
        )

        # 3. 组装元数据
        meta = PromptMeta(
            photo=photo,
            lighting=lighting,
            composition=composition,
            color=color,
            narrative=narrative,
            raw_prompt=prompt
        )

        return {
            "prompt": prompt,
            "meta": meta
        }

    def _match_style(self, genre: str) -> Optional[Dict[str, Any]]:
        """模糊匹配风格配置"""
        if not genre:
            return None

        # 精确匹配
        if genre in self.style_map:
            return self.style_map[genre]

        # 模糊匹配
        for key, config in self.style_map.items():
            if key in genre or genre in key:
                return config

        return None

    def _infer_photo_params(self, intent: IntentRepresentation) -> PhotoParams:
        """根据风格推断摄影参数"""
        config = self._match_style(intent.style.genre)
        if config and "photo" in config:
            p = config["photo"]
            return PhotoParams(
                focal_length=p.get("focal_length"),
                aperture=p.get("aperture"),
                color_temperature=p.get("color_temperature"),
                film_grain=p.get("film_grain")
            )

        # 默认：标准写实
        return PhotoParams(
            focal_length="50mm",
            aperture="f/2.8",
            color_temperature=5500
        )

    def _infer_lighting(self, intent: IntentRepresentation) -> LightingSetup:
        """推断光影设置"""
        config = self._match_style(intent.style.genre)
        if config and "lighting" in config:
            l = config["lighting"]
            return LightingSetup(
                direction=l.get("direction"),
                quality=l.get("quality"),
                key_light=l.get("key_light"),
                fill_light=l.get("fill_light"),
                rim_light=l.get("rim_light"),
                atmosphere=l.get("atmosphere")
            )

        # 默认：自然光
        return LightingSetup(
            direction="自然光",
            quality="软",
            atmosphere="自然氛围"
        )

    def _infer_composition(self, intent: IntentRepresentation) -> CompositionRules:
        """从用户输入或意图中推断构图"""
        user_input = intent.subject.entity or ""

        # 尝试匹配构图关键词
        for key, config in self.composition_map.items():
            if key in user_input:
                return CompositionRules(
                    shot_size=config.get("shot_size"),
                    angle=config.get("angle"),
                    rule=config.get("rule")
                )

        # 尝试从风格配置推断
        config = self._match_style(intent.style.genre)
        if config and "composition" in config:
            c = config["composition"]
            return CompositionRules(
                shot_size=c.get("shot_size"),
                angle=c.get("angle"),
                rule=c.get("rule")
            )

        # 默认
        return CompositionRules(
            shot_size="中景",
            angle="平视",
            rule="三分法"
        )

    def _infer_color(self, intent: IntentRepresentation) -> ColorScience:
        """推断色彩方案"""
        config = self._match_style(intent.style.genre)
        if config and "color" in config:
            c = config["color"]
            return ColorScience(
                dominant_hue=c.get("dominant_hue"),
                complementary=c.get("complementary"),
                hex_codes=c.get("hex_codes"),
                film_stock=c.get("film_stock")
            )

        return ColorScience(
            dominant_hue="自然色",
            film_stock=None
        )

    def _generate_narrative(self, intent: IntentRepresentation) -> str:
        """
        生成叙事描述
        把"酷炫"变成"一个赛博朋克战士在雨夜霓虹中回眸的瞬间"
        """
        config = self._match_style(intent.style.genre)
        if config and "narrative" in config:
            template = config["narrative"]
            # 替换主体占位符
            return template.replace("在", f"{intent.subject.entity}在", 1)

        # 通用叙事
        subject = intent.subject.entity
        mood = intent.style.mood
        genre = intent.style.genre

        if mood:
            return f"{subject}在{mood}的氛围中，画面充满情感张力"
        if genre:
            return f"{subject}在{genre}风格的独特呈现中"

        return f"{subject}的高质量呈现"

    def _build_seedream_prompt(
            self,
            intent: IntentRepresentation,
            photo: PhotoParams,
            lighting: LightingSetup,
            composition: CompositionRules,
            color: ColorScience,
            narrative: str
    ) -> str:
        """构建 Seedream 中文提示词"""
        parts = []

        # === 主体描述（最优先）===
        subject_parts = []
        if intent.subject.entity:
            subject_parts.append(intent.subject.entity)
        if intent.subject.attributes:
            subject_parts.extend(intent.subject.attributes)
        if intent.subject.pose:
            subject_parts.append(intent.subject.pose)
        if intent.subject.expression:
            subject_parts.append(f"表情{intent.subject.expression}")
        if subject_parts:
            parts.append("，".join(subject_parts))

        # === 风格与氛围 ===
        style_parts = []
        if intent.style.genre:
            style_parts.append(f"{intent.style.genre}风格")
        if intent.style.references:
            style_parts.append(f"参考{', '.join(intent.style.references)}")
        if intent.style.mood:
            style_parts.append(f"{intent.style.mood}氛围")
        if style_parts:
            parts.append("，".join(style_parts))

        # === 摄影参数 ===
        photo_parts = []
        if photo.focal_length:
            photo_parts.append(f"{photo.focal_length}焦段")
        if photo.aperture:
            photo_parts.append(f"光圈{photo.aperture}")
        if photo.color_temperature:
            photo_parts.append(f"色温{photo.color_temperature}K")
        if photo.film_grain:
            photo_parts.append(f"{photo.film_grain}胶片质感")
        if photo_parts:
            parts.append("，".join(photo_parts) + "拍摄")

        # === 光影 ===
        light_parts = []
        if lighting.direction:
            light_parts.append(lighting.direction)
        if lighting.quality:
            light_parts.append(f"{lighting.quality}质感光线")
        if lighting.key_light:
            light_parts.append(f"主光{lighting.key_light}")
        if lighting.fill_light:
            light_parts.append(f"补光{lighting.fill_light}")
        if lighting.rim_light:
            light_parts.append(f"轮廓光{lighting.rim_light}")
        if lighting.atmosphere:
            light_parts.append(lighting.atmosphere)
        if light_parts:
            parts.append("，".join(light_parts))

        # === 构图 ===
        comp_parts = []
        if composition.shot_size:
            comp_parts.append(f"{composition.shot_size}构图")
        if composition.angle:
            comp_parts.append(f"{composition.angle}视角")
        if composition.rule:
            comp_parts.append(f"采用{composition.rule}")
        if comp_parts:
            parts.append("，".join(comp_parts))

        # === 色彩 ===
        color_parts = []
        if color.dominant_hue:
            color_parts.append(f"主色调{color.dominant_hue}")
        if color.complementary:
            color_parts.append(f"搭配{color.complementary}")
        if color.film_stock:
            color_parts.append(f"{color.film_stock}色彩")
        if color.hex_codes:
            color_parts.append(f"色值{', '.join(color.hex_codes)}")
        if color_parts:
            parts.append("，".join(color_parts))

        # === 叙事（点睛之笔）===
        if narrative:
            parts.append(f"画面叙事：{narrative}")

        # === 质量约束 ===
        if intent.output.quality == "high":
            parts.append("超精细，8K分辨率，专业摄影，极致光影")
        elif intent.output.quality == "medium":
            parts.append("高质量，清晰细节")

        # === 必须包含 / 避免 ===
        if intent.constraints.must_include:
            parts.append("必须包含：" + "，".join(intent.constraints.must_include))
        if intent.constraints.avoid:
            parts.append("避免出现：" + "，".join(intent.constraints.avoid))

        return "，".join(parts)