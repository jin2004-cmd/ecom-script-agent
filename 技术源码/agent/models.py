"""核心数据结构定义。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Product:
    """商品信息，作为脚本生成的输入。"""

    name: str
    category: str = "general"
    price: float = 39.9
    selling_points: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)
    target_audience: str = "目标人群"
    brand: str = ""
    trust_proof: str = ""
    promo: str = ""
    medical: bool = False

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "selling_points": self.selling_points,
            "pain_points": self.pain_points,
            "target_audience": self.target_audience,
            "brand": self.brand,
            "trust_proof": self.trust_proof,
            "promo": self.promo,
            "medical": self.medical,
        }


@dataclass
class ComplianceIssue:
    """单条合规问题。"""

    rule_id: str
    word: str
    message: str
    severity: str
    suggestion: str

    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "word": self.word,
            "message": self.message,
            "severity": self.severity,
            "suggestion": self.suggestion,
        }


@dataclass
class Shot:
    """分镜单元。"""

    time_range: str
    scene: str
    subtitle: str
    voiceover: str

    def to_dict(self) -> Dict:
        return {
            "time_range": self.time_range,
            "scene": self.scene,
            "subtitle": self.subtitle,
            "voiceover": self.voiceover,
        }


@dataclass
class Script:
    """一份完整的带货脚本（口播文案 + 分镜 + 合规结果）。"""

    title: str
    hook_type: str
    structure_name: str
    voiceover: str
    shots: List[Shot]
    compliance: Dict
    meta: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "hook_type": self.hook_type,
            "structure_name": self.structure_name,
            "voiceover": self.voiceover,
            "shots": [s.to_dict() for s in self.shots],
            "compliance": self.compliance,
            "meta": self.meta,
        }