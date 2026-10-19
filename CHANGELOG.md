# Changelog

All notable changes to the e-commerce viral script agent are recorded here.

> First entry. The repository carried no version marker, so this file opens at **v1.0.0**.

## 2026-10-19 — v1.0.0

### Added

- `CHANGELOG.md` (this file).

### Verified in this pass

Every number printed in `README.md` was re-counted against the repository rather than trusted:

| README claim | Source of truth | Result |
|---|---|---|
| 原稿库 **19 篇**（痛点 6 / 反差 6 / 场景 7） | `data/original_scripts/{pain,reverse,scenario}.json` → `originals[]` | ✅ 6 / 6 / 7 = 19 |
| **27 个单元测试** | `def test_` across `技术源码/tests/*.py` | ✅ 27（5 + 5 + 9 + 8） |
| `技术源码/agent/` 是 **9 个模块** | directory listing | ✅ 9 |
| 合规引擎 **4 条违禁词规则** | `data/compliance_rules.json` → `banned_words[]` | ✅ 4（通用 2 + 医疗 2） |
| **27 条自动替换** | `data/compliance_rules.json` → `auto_fix{}` | ✅ 27 entries |
| 医疗合规提示语 | `required_disclaimers.medical` | ✅ 2 条 |

Confirmed on `main`: `电商爆款脚本生成智能体-一键出稿版.html` (51,820 B, the file the README calls
the main deliverable), `脚本生成智能体-可视化演示版.html` (26,174 B, the kept older build),
`00-项目展示首页.html`, four `examples/` formats for both demo products, and the three `截图/`
files referenced by the showcase page. GitHub Pages: enabled, `status: built`.

### Note on a number that is easy to misread

`27` appears **twice in this project with two unrelated meanings**, and both are real:

- `data/compliance_rules.json` → `auto_fix` has **27** replacement entries.
- `技术源码/tests/` has **27** unit-test functions.

They are not the same 27. A portfolio page once quoted "27 条自动替换" and was later "corrected"
to "27 个单元测试" on the assumption that only one of the two existed. Both exist. This note is
here so the same mistake is not made a third time.

### Known gaps

- **The headline performance numbers are small-sample and are labelled as such in the README**
  ("实习团队小范围灰度一周、3 人样本（团队周报口径）": 7-9 → 15-18 条/人/日, 8-12 → 2-3 分钟/条,
  过审率约 70% → 82%). They were not re-derived from any dashboard during this pass; the README's
  own caveat is the accurate framing.
- **`00-项目展示首页.html` and `index.html` are byte-identical at 719,654 B.** Both are kept, which
  doubles the largest file in the repo for no functional gain. Not changed here — deleting one is a
  behaviour change, not a bug fix.
- `docs/演示说明.md` and `docs/项目说明.md` were not opened and re-read in this pass.
- The Python CLI's four test files were counted, not executed (`python -m unittest discover` was
  not run here).
