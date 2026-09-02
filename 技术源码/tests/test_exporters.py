"""导出器测试：Markdown / CSV / JSON / HTML。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent.exporters import export_all, script_to_markdown, scripts_to_csv, scripts_to_html, scripts_to_json
from agent.generator import ScriptGenerator
from agent.models import Product


def make_scripts(count: int = 3):
    product = Product(
        name="草本温灸肠胃贴",
        category="医疗保健",
        price=39.9,
        selling_points=["草本恒温发热", "持续温灸8小时"],
        pain_points=["肚子着凉胀气", "久坐胃胀"],
        trust_proof="已通过相关资质备案",
        promo="第二件半价",
        medical=True,
    )
    return ScriptGenerator().generate(product, count=count, seed=1)


class ExporterTest(unittest.TestCase):
    def test_markdown_contains_key_sections(self) -> None:
        md = script_to_markdown(make_scripts(1)[0])
        self.assertIn("口播文案", md)
        self.assertIn("分镜脚本", md)
        self.assertIn("合规结果", md)

    def test_csv_row_count(self) -> None:
        csv_text = scripts_to_csv(make_scripts(3))
        rows = [line for line in csv_text.splitlines() if line.strip()]
        self.assertEqual(len(rows), 4)  # header + 3

    def test_json_roundtrip(self) -> None:
        data = scripts_to_json(make_scripts(2))
        self.assertEqual(len(data["scripts"]), 2)
        self.assertIn("voiceover", data["scripts"][0])

    def test_html_contains_scripts(self) -> None:
        html_text = scripts_to_html(make_scripts(2))
        self.assertIn("<!DOCTYPE html>", html_text)
        self.assertIn("方案1", html_text)

    def test_export_all_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            saved = export_all(make_scripts(2), Path(tmp), prefix="demo", formats=("md", "json", "csv", "html"))
            self.assertEqual(len(saved), 4)
            for path in saved:
                self.assertTrue(path.exists())
            json.loads((Path(tmp) / "demo.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()