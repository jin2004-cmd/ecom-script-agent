"""合规引擎测试：检测、医疗强校验、自动修正。"""

from __future__ import annotations

import unittest

from agent.compliance import ComplianceChecker


class ComplianceCheckerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = ComplianceChecker()

    def test_ads_absolute_words_flagged_for_all(self) -> None:
        issues = self.checker.check("这是全网最低价，效果最好", medical=False)
        self.assertGreaterEqual(len(issues), 1)
        self.assertTrue(any(issue.rule_id == "ads_absolute" for issue in issues))

    def test_medical_cure_words_flagged_only_for_medical(self) -> None:
        text = "这款产品可以根治胃病"
        self.assertEqual(len(self.checker.check(text, medical=False)), 0)
        issues = self.checker.check(text, medical=True)
        self.assertGreaterEqual(len(issues), 1)
        self.assertTrue(any(issue.rule_id == "medical_cure" for issue in issues))

    def test_fix_replaces_banned_words(self) -> None:
        text = "一贴见效，药到病除，保证有效"
        fixed, remaining, replaced = self.checker.fix(text, medical=True)
        self.assertGreaterEqual(len(replaced), 2)
        self.assertNotIn("药到病除", fixed)
        self.assertNotIn("一贴见效", fixed)
        self.assertEqual(len(remaining), 0)

    def test_disclaimers_for_medical(self) -> None:
        self.assertGreater(len(self.checker.disclaimers(medical=True)), 0)
        self.assertEqual(len(self.checker.disclaimers(medical=False)), 0)

    def test_summarize_passed(self) -> None:
        summary = self.checker.summarize([])
        self.assertTrue(summary["passed"])
        self.assertEqual(summary["issue_count"], 0)


if __name__ == "__main__":
    unittest.main()