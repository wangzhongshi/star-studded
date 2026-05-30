from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


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
    intensity: float = 0.5  # 0-1


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