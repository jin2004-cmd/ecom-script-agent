"""LLM 模式测试：提示词构建与返回解析（不联网，不依赖 API Key）。

背景：v1.0.4 之前 _build_system_prompt / _build_user_prompt 被 generate_with_llm
调用但从未定义，LLM 模式必然 NameError，而原有 27 个测试全部只覆盖模板路径，
因此这个缺口一直没被发现。本文件专门补上模型路径的回归用例。
"""

from __future__ import annotations

import unittest

from agent.compliance import ComplianceChecker
from agent.llm import (
    _build_system_prompt,
    _build_user_prompt,
    _parse_scripts,
)
from agent.models import Product
from agent.templates import TemplateLibrary


def _product(medical: bool = False) -> Product:
    return Product(
        name="草本温灸肠胃贴",
        category="health",
        price=59.0,
        selling_points=["温热舒缓", "独立包装"],
        pain_points=["久坐腹部发凉", "换季不适"],
        target_audience="久坐上班族",
        brand="暖记",
        trust_proof="十万用户复购",
        promo="第二件半价",
        medical=medical,
    )


class LlmPromptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.library = TemplateLibrary()
        cls.compliance = ComplianceChecker()

    def test_system_prompt_embeds_library_names(self) -> None:
        prompt = _build_system_prompt(self.library)
        for name in self.library.hook_names():
            self.assertIn(name, prompt)
        for name in self.library.structure_names():
            self.assertIn(name, prompt)

    def test_system_prompt_declares_output_schema(self) -> None:
        prompt = _build_system_prompt(self.library)
        self.assertIn('"scripts"', prompt)
        self.assertIn('"voiceover"', prompt)
        self.assertIn('"shots"', prompt)

    def test_user_prompt_carries_product_and_count(self) -> None:
        prompt = _build_user_prompt(_product(), 3, self.library)
        self.assertIn("草本温灸肠胃贴", prompt)
        self.assertIn("久坐上班族", prompt)
        self.assertIn("3", prompt)
        self.assertIn("温热舒缓", prompt)

    def test_user_prompt_marks_medical_only_for_medical(self) -> None:
        self.assertIn("医疗", _build_user_prompt(_product(medical=True), 1, self.library))
        self.assertNotIn("医疗", _build_user_prompt(_product(medical=False), 1, self.library))

    def test_parse_scripts_fixes_banned_words(self) -> None:
        # "保证有效" 在 data/compliance_rules.json 的 auto_fix 里有明确映射
        payload = {
            "scripts": [
                {
                    "title": "方案1",
                    "hook_type": "痛点直击",
                    "structure": "千川经典五段式",
                    "voiceover": "这款贴保证有效，坚持使用改善",
                    "shots": [{"time_range": "0-3s", "scene": "特写", "subtitle": "暖", "voiceover": "开场"}],
                }
            ]
        }
        scripts = _parse_scripts(payload, _product(), self.compliance, auto_fix=True)
        self.assertEqual(len(scripts), 1)
        self.assertEqual(scripts[0].meta["mode"], "llm")
        self.assertNotIn("保证有效", scripts[0].voiceover)
        self.assertIn("多数用户反馈有效", scripts[0].voiceover)
        self.assertTrue(scripts[0].compliance["passed"])
        self.assertIn("保证有效", scripts[0].meta["replaced"][0]["word"])

    def test_parse_scripts_without_autofix_keeps_issues(self) -> None:
        payload = {
            "scripts": [
                {
                    "title": "方案1",
                    "hook_type": "痛点直击",
                    "structure": "千川经典五段式",
                    "voiceover": "这是全网最低价",
                    "shots": [],
                }
            ]
        }
        scripts = _parse_scripts(payload, _product(), self.compliance, auto_fix=False)
        self.assertFalse(scripts[0].compliance["passed"])
        self.assertGreater(scripts[0].compliance["issue_count"], 0)

    def test_parse_scripts_appends_medical_disclaimers(self) -> None:
        payload = {
            "scripts": [
                {
                    "title": "方案1",
                    "hook_type": "痛点直击",
                    "structure": "千川经典五段式",
                    "voiceover": "温热舒缓，日常护理好物",
                    "shots": [],
                }
            ]
        }
        scripts = _parse_scripts(payload, _product(medical=True), self.compliance, auto_fix=True)
        self.assertIn("（合规提示）", scripts[0].voiceover)
        self.assertGreater(len(scripts[0].meta["disclaimers"]), 0)

    def test_parse_scripts_handles_empty_payload(self) -> None:
        self.assertEqual(_parse_scripts({}, _product(), self.compliance, auto_fix=True), [])


if __name__ == "__main__":
    unittest.main()
