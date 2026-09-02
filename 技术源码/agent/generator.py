"""模板模式脚本生成器：基于爆款结构模板库组合生成带货脚本。"""

from __future__ import annotations

import random
from typing import List, Optional, Tuple

from .compliance import ComplianceChecker
from .models import Product, Script, Shot
from .templates import TemplateLibrary


def _format_price(price: float) -> str:
    return str(int(price)) if float(price).is_integer() else str(price)


def _fill(template: str, product: Product, rng: random.Random) -> str:
    """把商品信息填充进模板占位符。"""
    kwargs = {
        "商品": product.name,
        "价格": _format_price(product.price),
        "痛点": rng.choice(product.pain_points) if product.pain_points else "生活小烦恼",
        "卖点": rng.choice(product.selling_points) if product.selling_points else "好用",
        "人群": product.target_audience,
        "品牌": product.brand or "这款产品",
        "背书": product.trust_proof or "众多用户真实体验反馈",
        "优惠": product.promo or "限时优惠",
        "限量": str(rng.randint(30, 100)),
    }
    return template.format(**kwargs)


class ScriptGenerator:
    """模板模式：数据驱动、零外部依赖、可复现（seed 控制随机）。"""

    def __init__(self, templates: Optional[TemplateLibrary] = None, compliance: Optional[ComplianceChecker] = None) -> None:
        self.templates = templates or TemplateLibrary()
        self.compliance = compliance or ComplianceChecker()

    def generate(
        self,
        product: Product,
        count: int = 5,
        seed: Optional[int] = None,
        auto_fix: bool = True,
    ) -> List[Script]:
        if count < 1:
            raise ValueError("count 必须大于 0")
        rng = random.Random(seed)
        return [self._generate_one(product, rng, auto_fix, index) for index in range(count)]

    def _generate_one(self, product: Product, rng: random.Random, auto_fix: bool, index: int) -> Script:
        hook, structure, cta, lines = self._build_segments(product, rng, index)
        section_lines = self._lines_for_structure(lines, structure)

        voiceover = "\n".join(section_lines)
        disclaimers = self.compliance.disclaimers(medical=product.medical)
        if disclaimers:
            voiceover += "\n\n" + "\n".join("（合规提示）" + line for line in disclaimers)

        if auto_fix:
            voiceover, remaining, replaced = self.compliance.fix(voiceover, medical=product.medical)
        else:
            remaining = self.compliance.check(voiceover, medical=product.medical)
            replaced = []

        shots = [
            Shot(
                time_range=section["duration"],
                scene=section["scene"],
                subtitle=_shorten(line),
                voiceover=line,
            )
            for section, line in zip(structure["sections"], section_lines)
        ]

        compliance = self.compliance.summarize(remaining)
        compliance["disclaimers"] = disclaimers
        meta = {
            "mode": "template",
            "seed_group": index,
            "replaced": [{"word": w, "to": r} for w, r in replaced],
        }

        return Script(
            title=f"方案{index + 1}｜{hook['name']} · {product.name}",
            hook_type=hook["name"],
            structure_name=structure["name"],
            voiceover=voiceover,
            shots=shots,
            compliance=compliance,
            meta=meta,
        )

    def _build_segments(self, product: Product, rng: random.Random, index: int = 0) -> Tuple[dict, dict, dict, List[str]]:
        hook = self.templates.hooks[(rng.randrange(len(self.templates.hooks)) + index) % len(self.templates.hooks)]
        structure = self.templates.structures[(rng.randrange(len(self.templates.structures)) + index) % len(self.templates.structures)]
        cta = self.templates.random_cta(rng)

        hook_line = _fill(hook["template"], product, rng)

        pains = rng.sample(product.pain_points, k=min(3, len(product.pain_points)))
        pain_line = "你" + "、".join(pains) + "……这些场景是不是都经历过？"

        points = rng.sample(product.selling_points, k=min(3, len(product.selling_points)))
        intro_line = "今天给你带来" + product.name + "：" + "、".join(points) + "，帮你把这些烦恼一个个搞定。"

        trust_line = (product.trust_proof or "众多用户真实体验反馈") + "。"

        cta_line = _fill(cta["template"], product, rng)

        return hook, structure, cta, [hook_line, pain_line, intro_line, trust_line, cta_line]

    @staticmethod
    def _lines_for_structure(lines: List[str], structure: dict) -> List[str]:
        section_count = len(structure["sections"])
        if section_count == 5:
            return lines
        if section_count == 3:
            return [lines[0], lines[2], lines[4]]
        return lines[:section_count]


def _shorten(text: str, limit: int = 30) -> str:
    return text if len(text) <= limit else text[:limit] + "…"