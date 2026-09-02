"""合规校验引擎：违禁词检测、医疗品类强校验、自动替换。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import ComplianceIssue


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class ComplianceChecker:
    """基于 data/compliance_rules.json 的规则化合规引擎。

    覆盖两层能力：
    1. 通用层：广告法绝对化用语、夸大承诺类表述；
    2. 医疗品类强校验：功效夸大、绝对化医疗承诺，并自动附加合规提示语。
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or (DATA_DIR / "compliance_rules.json")
        with open(self.path, encoding="utf-8-sig") as f:
            raw = json.load(f)
        self._rules: List[Dict] = raw["banned_words"]
        self.auto_fix: Dict[str, str] = raw.get("auto_fix", {})
        self.required_disclaimers: Dict[str, List[str]] = raw.get("required_disclaimers", {})

    def check(self, text: str, medical: bool = False) -> List[ComplianceIssue]:
        """检测文本中的合规问题，返回问题列表。"""
        issues: List[ComplianceIssue] = []
        for rule in self._rules:
            if rule.get("scope") == "medical" and not medical:
                continue
            pattern = rule["pattern"]
            for match in re.finditer(pattern, text):
                issues.append(
                    ComplianceIssue(
                        rule_id=rule["id"],
                        word=match.group(0),
                        message=rule["message"],
                        severity=rule["severity"],
                        suggestion=rule.get("suggestion", ""),
                    )
                )
        return issues

    def fix(self, text: str, medical: bool = False) -> Tuple[str, List[ComplianceIssue], List[Tuple[str, str]]]:
        """自动替换可修复的违禁表述，返回 (修复后文本, 剩余问题, 替换记录)。"""
        fixed = text
        replaced: List[Tuple[str, str]] = []
        for word, repl in sorted(self.auto_fix.items(), key=lambda item: -len(item[0])):
            if word and repl is not None and word in fixed:
                fixed = fixed.replace(word, repl)
                replaced.append((word, repl))
        remaining = self.check(fixed, medical=medical)
        return fixed, remaining, replaced

    def disclaimers(self, medical: bool = False) -> List[str]:
        """返回当前品类需要附加的合规提示语。"""
        if medical:
            return list(self.required_disclaimers.get("medical", []))
        return []

    def summarize(self, issues: List[ComplianceIssue]) -> Dict:
        """把问题列表整理成可写进脚本的合规结果。"""
        passed = len(issues) == 0
        return {
            "passed": passed,
            "issue_count": len(issues),
            "issues": [issue.to_dict() for issue in issues],
        }