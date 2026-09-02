"""模板库完整性测试。"""

from __future__ import annotations

import unittest

from agent.templates import TemplateLibrary


class TemplateLibraryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.library = TemplateLibrary()

    def test_hooks_non_empty(self) -> None:
        self.assertGreater(len(self.library.hooks), 0)

    def test_hook_required_fields(self) -> None:
        for hook in self.library.hooks:
            self.assertIn("id", hook)
            self.assertIn("name", hook)
            self.assertIn("template", hook)

    def test_hook_templates_placeholders_are_fillable(self) -> None:
        for hook in self.library.hooks:
            template = hook["template"]
            for placeholder in ("{商品}", "{价格}", "{痛点}", "{卖点}", "{人群}", "{品牌}", "{背书}", "{优惠}", "{限量}"):
                template = template.replace(placeholder, "")
            self.assertNotIn("{", template)

    def test_structures_have_sections_with_duration(self) -> None:
        for structure in self.library.structures:
            self.assertGreater(len(structure["sections"]), 0)
            for section in structure["sections"]:
                self.assertIn("name", section)
                self.assertIn("duration", section)
                self.assertIn("scene", section)

    def test_cta_non_empty(self) -> None:
        self.assertGreater(len(self.library.ctas), 0)

    def test_pick_by_id(self) -> None:
        first = self.library.hooks[0]
        self.assertEqual(self.library.hook(first["id"])["id"], first["id"])

    def test_pick_unknown_raises(self) -> None:
        with self.assertRaises(KeyError):
            self.library.hook("not-exists")

    def test_load_json_with_bom(self) -> None:
        """Windows 记事本保存的 UTF-8 BOM 文件也必须能正常加载。"""
        import json
        import tempfile
        from pathlib import Path
        from agent.templates import DATA_DIR, TemplateLibrary
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "templates.json"
            raw = (DATA_DIR / "templates.json").read_bytes()
            target.write_bytes(b"\xef\xbb\xbf" + raw)
            library = TemplateLibrary(target)
            self.assertGreater(len(library.hooks), 0)


if __name__ == "__main__":
    unittest.main()