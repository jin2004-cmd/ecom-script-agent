# Changelog

All notable changes to the e-commerce viral script agent are recorded here.

> First entry. The repository carried no version marker, so this file opens at **v1.0.0**.

## 2026-10-21 — v1.0.1

### Fixed

- **LLM 模式此前必然崩溃（`NameError`）。** `技术源码/agent/llm.py` 的 `generate_with_llm()`
  调用了 `_build_system_prompt(library)` 与 `_build_user_prompt(product, count, library)`，
  但这两个函数在整个仓库里**从未定义**。任何一次 `--mode llm` 调用都会在执行到
  payload 构造时抛出 `NameError: name '_build_system_prompt' is not defined`。
  已补上两个函数的实现：
  - `_build_system_prompt()` —— 角色设定、JSON 输出结构（与 `response_format: json_object`
    对齐）、广告法/医疗合规红线、从 `data/templates.json` 动态注入的可用钩子与结构名；
  - `_build_user_prompt()` —— 商品信息、生成数量、差异化要求，医疗品类追加特别提醒。
- **LLM 模式的合规处理与模板模式此前不一致。** 模板模式会走 `auto_fix` 自动替换并追加
  医疗合规提示语，LLM 模式只 `check` 不 `fix`、也不加提示语。现在抽取 `_parse_scripts()`
  统一处理，两种模式行为一致；`generate_with_llm()` 新增 `auto_fix` 参数（默认 `True`），
  `cli.py` 的 `--no-fix` 现在对 LLM 模式同样生效。
- 顺带修正：`cli.py` 此前把 `--no-fix` 只传给模板模式分支，LLM 分支完全忽略该参数。

### Added

- `技术源码/tests/test_llm.py` —— **8 个**单元测试，专门覆盖此前完全没有测试的模型路径：
  提示词是否注入模板库名称与输出结构、商品信息与数量是否正确传递、医疗标记是否只在
  医疗品类出现、返回解析是否执行自动替换、关闭 `auto_fix` 时是否保留问题、医疗提示语
  是否追加、空载荷是否安全返回。**全部不联网、不需要 API Key**（只测提示词构建与
  `_parse_scripts()` 解析，不触碰 `requests`）。

### Changed

- 单元测试函数总数 **27 → 35**（5 + 5 + 9 + 8 + 8）。`README.md` 中三处「27 个单元测试」
  及「4 个测试文件」已同步为 35 / 5。

### Why it went unnoticed

原有 27 个测试**全部只覆盖模板路径**，没有一个 import 过 `agent.llm`。测试全绿，
但绿色的是没被走过的那条路。这也是本次专门补模型路径回归用例的原因。

### Note on the two 27s (updated)

上一版记录过「`27` 在本项目里出现两次、含义不同且都为真」：
`auto_fix` 的 **27 条替换规则** 与 `技术源码/tests/` 的 **27 个测试函数**。
**测试函数数现已变为 35，两者不再数值相同，这条容易混淆的巧合就此消失。**
`auto_fix` 的 27 条替换规则不变。

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
