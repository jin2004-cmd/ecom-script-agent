"""爆款结构提示词模板库：加载与管理钩子/结构/CTA 模板。"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Optional


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class TemplateLibrary:
    """从 data/templates.json 加载模板库，并提供按需取用能力。"""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or (DATA_DIR / "templates.json")
        with open(self.path, encoding="utf-8-sig") as f:
            raw = json.load(f)
        self.hooks: List[Dict] = raw["hooks"]
        self.structures: List[Dict] = raw["structures"]
        self.ctas: List[Dict] = raw["cta"]

    def hook(self, hook_id: Optional[str] = None) -> Dict:
        return self._pick(self.hooks, hook_id)

    def structure(self, structure_id: Optional[str] = None) -> Dict:
        return self._pick(self.structures, structure_id)

    def cta(self, cta_id: Optional[str] = None) -> Dict:
        return self._pick(self.ctas, cta_id)

    def random_hook(self, rng: random.Random) -> Dict:
        return rng.choice(self.hooks)

    def random_structure(self, rng: random.Random) -> Dict:
        return rng.choice(self.structures)

    def random_cta(self, rng: random.Random) -> Dict:
        return rng.choice(self.ctas)

    def hook_names(self) -> List[str]:
        return [h["name"] for h in self.hooks]

    def structure_names(self) -> List[str]:
        return [s["name"] for s in self.structures]

    @staticmethod
    def _pick(items: List[Dict], item_id: Optional[str]) -> Dict:
        if item_id is None:
            return items[0]
        for item in items:
            if item.get("id") == item_id:
                return item
        raise KeyError(f"模板不存在: {item_id}")