from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import json


class IntentMode(Enum):
    STYLE_TRANSFER = "style_transfer"
    ELEMENT_SWAP = "element_swap"
    MOOD_SHIFT = "mood_shift"
    REPLICATE = "replicate"
    COMPOSITE = "composite"


@dataclass
class Subject:
    entity: str = ""
    attributes: List[str] = field(default_factory=list)
    pose: str = ""
    expression: str = ""


@dataclass
class Style:
    genre: str = ""
    references: List[str] = field(default_factory=list)
    mood: str = ""
    intensity: float = 0.5


@dataclass
class Output:
    format: str = "image"
    aspect_ratio: str = "1:1"
    quality: str = "high"


@dataclass
class Constraints:
    must_include: List[str] = field(default_factory=list)
    avoid: List[str] = field(default_factory=list)


@dataclass
class IntentRepresentation:
    mode: IntentMode = IntentMode.STYLE_TRANSFER
    subject: Subject = field(default_factory=Subject)
    style: Style = field(default_factory=Style)
    output: Output = field(default_factory=Output)
    constraints: Constraints = field(default_factory=Constraints)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "subject": {
                "entity": self.subject.entity,
                "attributes": self.subject.attributes or [],
                "pose": self.subject.pose or "",
                "expression": self.subject.expression or ""
            },
            "style": {
                "genre": self.style.genre or "",
                "references": self.style.references or [],
                "mood": self.style.mood or "",
                "intensity": self.style.intensity
            },
            "output": {
                "format": self.output.format or "image",
                "aspect_ratio": self.output.aspect_ratio or "1:1",
                "quality": self.output.quality or "high"
            },
            "constraints": {
                "must_include": self.constraints.must_include or [],
                "avoid": self.constraints.avoid or []
            }
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "IntentRepresentation":
        mode_map = {
            "style_transfer": IntentMode.STYLE_TRANSFER,
            "element_swap": IntentMode.ELEMENT_SWAP,
            "mood_shift": IntentMode.MOOD_SHIFT,
            "replicate": IntentMode.REPLICATE,
            "composite": IntentMode.COMPOSITE
        }

        return cls(
            mode=mode_map.get(data.get("mode", "style_transfer"), IntentMode.STYLE_TRANSFER),
            subject=Subject(
                entity=data.get("subject", {}).get("entity", ""),
                attributes=data.get("subject", {}).get("attributes", []) or [],
                pose=data.get("subject", {}).get("pose", ""),
                expression=data.get("subject", {}).get("expression", "")
            ),
            style=Style(
                genre=data.get("style", {}).get("genre", ""),
                references=data.get("style", {}).get("references", []) or [],
                mood=data.get("style", {}).get("mood", ""),
                intensity=data.get("style", {}).get("intensity", 0.5)
            ),
            output=Output(
                format=data.get("output", {}).get("format", "image"),
                aspect_ratio=data.get("output", {}).get("aspect_ratio", "1:1"),
                quality=data.get("output", {}).get("quality", "high")
            ),
            constraints=Constraints(
                must_include=data.get("constraints", {}).get("must_include", []) or [],
                avoid=data.get("constraints", {}).get("avoid", []) or []
            )
        )