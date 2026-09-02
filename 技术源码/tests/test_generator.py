"""模板模式生成器测试：输出完整性、合规、可复现。"""

from __future__ import annotations

import unittest

from agent.compliance import ComplianceChecker
from agent.generator import ScriptGenerator
from agent.models import Product
from agent.templates import TemplateLibrary


def make_medical_product() -> Product:
    return Product(
        name="草本温灸肠胃贴",
        category="医疗保健",
        price=39.9,
        selling_points=["草本恒温发热", "持续温灸8小时", "医用级无纺布不粘毛", "一撕一贴全家适用"],
        pain_points=["肚子着凉胀气", "久坐办公室胃胀不消化", "老人小孩肠胃敏感"],
        target_audience="上班久坐族、有老人小孩的家庭",
        trust_proof="已通过相关资质备案，累计服务百万用户",
        promo="第二件半价",
        medical=True,
    )


class ScriptGeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generator = ScriptGenerator()

    def test_generate_count(self) -> None:
        scripts = self.generator.generate(make_medical_product(), count=5, seed=42)
        self.assertEqual(len(scripts), 5)

    def test_titles_unique(self) -> None:
        scripts = self.generator.generate(make_medical_product(), count=5, seed=42)
        titles = [script.title for script in scripts]
        self.assertEqual(len(titles), len(set(titles)))

    def test_voiceover_and_shots_complete(self) -> None:
        scripts = self.generator.generate(make_medical_product(), count=5, seed=42)
        for script in scripts:
            self.assertTrue(script.voiceover.strip())
            self.assertGreaterEqual(len(script.shots), 3)
            for shot in script.shots:
                self.assertTrue(shot.time_range)
                self.assertTrue(shot.scene)
                self.assertTrue(shot.voiceover)

    def test_medical_compliance_passed_after_autofix(self) -> None:
        scripts = self.generator.generate(make_medical_product(), count=10, seed=7)
        for script in scripts:
            self.assertTrue(script.compliance["passed"], msg=script.voiceover)
            self.assertEqual(script.compliance["issue_count"], 0)

    def test_general_product_no_medical_disclaimer(self) -> None:
        product = Product(name="蓝牙耳机", category="3C数码", price=199.0, selling_points=["降噪"], pain_points=["噪音"], medical=False)
        scripts = self.generator.generate(product, count=1, seed=1)
        self.assertEqual(scripts[0].compliance.get("disclaimers"), [])

    def test_medical_product_has_disclaimer(self) -> None:
        scripts = self.generator.generate(make_medical_product(), count=1, seed=1)
        self.assertGreaterEqual(len(scripts[0].compliance.get("disclaimers", [])), 1)
        self.assertIn("不能代替药物", scripts[0].voiceover)

    def test_reproducible_with_seed(self) -> None:
        a = self.generator.generate(make_medical_product(), count=3, seed=99)
        b = self.generator.generate(make_medical_product(), count=3, seed=99)
        self.assertEqual([s.voiceover for s in a], [s.voiceover for s in b])

    def test_no_fix_keeps_issues(self) -> None:
        generator = ScriptGenerator()
        text_checker = ComplianceChecker()
        product = make_medical_product()
        product.pain_points = ["肚子疼"]
        product.selling_points = ["根治胃病"]
        scripts = generator.generate(product, count=1, seed=1, auto_fix=False)
        self.assertGreater(scripts[0].compliance["issue_count"], 0)

    def test_invalid_count_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.generator.generate(make_medical_product(), count=0)


if __name__ == "__main__":
    unittest.main()