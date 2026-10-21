# 电商短视频爆款脚本生成智能体（千川带货版）

<div align="center">

[![在线试用](https://img.shields.io/badge/在线试用-点开即用-4f6df5?style=for-the-badge)](https://jin2004-cmd.github.io/ecom-script-agent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge)](LICENSE)
[![零依赖](https://img.shields.io/badge/网页版-单HTML零依赖-22c55e?style=for-the-badge)](#一网页版一键出稿推荐开箱即用)

</div>

> 这个项目是被真实需求逼出来的：我在做 AI 内容运营实习时，团队一天要出十几条千川带货脚本，条条得过广告法，纯手写又慢又容易踩词。我就自己搭了这个 Agent——选模板、点按钮一键出稿，爆款框架保留、细节自动改写，出稿自动过合规校验。
>
> 🟢 **[在线试用（点开即用，不用装任何东西）](https://jin2004-cmd.github.io/ecom-script-agent/)** ｜ [一键出稿版](https://jin2004-cmd.github.io/ecom-script-agent/电商爆款脚本生成智能体-一键出稿版.html)
>
> 📂 源码：`技术源码/agent/`（Python 包，9 个模块）· `技术源码/tests/`（5 个测试文件）· `data/`（原稿库 / 模板 / 合规规则）· `examples/`（HTML/CSV/JSON/Markdown 四格式导出示例）

**先交代口径，免得数字看着像编的**：在实习团队小范围灰度一周、3 人样本（团队周报口径）——人均日产从 7-9 条提到 15-18 条，单条脚本 8-12 分钟降到 2-3 分钟，素材过审率约 70% 提到 82%。

- **网页版（推荐）**：单 HTML 文件，双击打开即用，零环境零依赖
- **模板模式**：零第三方依赖，Python 3.9+ 直接运行，可复现（seed 控制）
- **LLM 模式**：对接 OpenAI 兼容 Chat API（默认火山方舟 / 豆包），生成后仍强制过一遍本地合规引擎
- **合规引擎**：广告法绝对化用语检测 + 医疗品类功效夸大强校验 + 自动替换修正

> 项目介绍见 [docs/项目说明.md](docs/项目说明.md)；
> **给网页版加自己的爆款稿见 [docs/新增原稿操作说明.md](docs/新增原稿操作说明.md)**；
> 运行、配置与数据文件说明见 [docs/使用与调试指南.md](docs/使用与调试指南.md)。

---

## 一、网页版一键出稿（推荐，开箱即用）

**主交付文件**：电商爆款脚本生成智能体-一键出稿版.html（与 README 同级）

双击用浏览器打开即可，全程图形化操作，不需要 Python、命令行或联网。

1. 选择模板分类：痛点直击型 / 效果反差型 / 真实场景型（三选一）
2. 点「生成 1 条新脚本」或「批量生成 3 条」
3. 右侧直接出稿：完整带货脚本 + 合规校验结果，可一键复制 / 下载

内置能力：

- **原稿库**：内置 19 篇真实爆款原稿（痛点直击 6 / 效果反差 6 / 真实场景 7），分五段模块管理
- **改写引擎**：模块重组 + 同义替换 + 语序/语气微调，框架 100% 保留、细节不重复（与原稿和历史稿重复率 ≤60%）
- **合规自动化**：出稿自动替换违禁词、追加医疗合规提示语，输出即合规
- **原稿库管理**：左下角面板可直接粘贴自己的爆款稿入库，立即参与改写；支持导出/导入备份

> 旧版可视化演示版（脚本生成智能体-可视化演示版.html）保留并存，供对比参考。

## 二、命令行快速开始（进阶可选）

```bash
# 1. 进入项目目录
cd 技术源码

# 2. 跑通内置示例（肠胃贴 + 蓝牙耳机，各 5 条）
python -m agent demo

# 3. 查看生成结果
#    examples/demo/草本温灸肠胃贴.md / .html / .csv / .json
```

### 自定义商品生成

```bash
python -m agent generate \
  --product "暖颈贴" \
  --category "医疗保健" \
  --price 29.9 \
  --medical \
  --points "恒温发热" --points "轻薄无感" \
  --pains "低头族脖子酸痛" --pains "空调房受凉" \
  --audience "上班族" \
  --promo "买二送一" \
  --count 5 --seed 42 \
  --out examples/generated --prefix my_product
```

生成的文件默认包含 4 种格式：Markdown（可读）/ JSON（结构化）/ CSV（表格）/ HTML（可视化页面）。

## 三、常用命令

| 命令 | 说明 |
| --- | --- |
| python -m agent demo | 跑通内置示例商品，输出到 examples/demo/ |
| python -m agent generate ... | 根据商品信息生成脚本（模板模式） |
| python -m agent check --text "..." --medical | 单独检测一段文案的合规性 |
| python -m agent templates | 查看内置爆款结构模板库 |
| python -m agent products | 查看内置示例商品 |

## 四、LLM 模式（可选，火山方舟/豆包）

```bash
# 复制 .env.example 并填写
# ARK_API_KEY=...
# ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
# ARK_MODEL=doubao-pro-32k

pip install -r requirements.txt

python -m agent generate --product "草本温灸肠胃贴" --medical \
  --points "草本恒温发热" --points "持续温灸8小时" \
  --pains "肚子着凉胀气" --pains "久坐胃胀" \
  --mode llm --count 5
```

LLM 模式通过系统提示词注入「结构要求 + 合规红线」，生成结果仍会再过一遍本地合规引擎，双重保障。**模型负责写，规则负责拦**——这是我做这个项目时刻意分开的两件事。

## 五、核心设计

```
选模板（痛点直击 / 效果反差 / 真实场景）
        │
        ▼
┌──────────────────────────────────────────────┐
│ 原稿库（data/original_scripts/*.json）        │
│   · 每类 ≥5 篇真实爆款原稿，分五段模块        │
│   · hook 钩子 / pain 痛点 / product 卖点      │
│   · trust 背书 / cta 结尾                     │
└──────────────────────────────────────────────┘
        │  模块重组 + 轻量改写（同义替换/语序/语气）
        ▼
┌──────────────────────────────────────────────┐
│ 合规引擎（data/compliance_rules.json）        │
│   · 广告法绝对化用语检测                      │
│   · 医疗品类功效夸大强校验                    │
│   · 自动替换 + 合规提示语附加                 │
└──────────────────────────────────────────────┘
        │  去重校验（与原稿/历史稿重复率 ≤60%）
        ▼
输出：完整带货脚本 + 合规结果（可复制/下载）
```

### 目录结构

```
作品集-爆款脚本生成智能体/
├── 00-项目展示首页.html    # 作品集展示首页（HR 先看这个）
├── 电商爆款脚本生成智能体-一键出稿版.html   # 主交付：网页版一键出稿（双击即用）
├── 脚本生成智能体-可视化演示版.html # 旧版可视化演示（并存）
├── data/
│   ├── original_scripts/    # 爆款原稿库（pain/reverse/scenario 三类）
│   ├── templates.json        # 爆款结构提示词模板库
│   ├── compliance_rules.json # 合规规则与自动替换表
│   └── products.json         # 内置示例商品
├── examples/           # 已生成的示例输出（温胆胃肠贴/蓝牙耳机）
├── 截图/              # 作品集展示截图（首页内嵌同款）
├── docs/
│   ├── 演示说明.md          # 100 字极简演示说明（作品集用）
│   ├── 新增原稿操作说明.md  # 怎么加自己的爆款稿
│   └── 项目说明.md          # 项目介绍（一页纸）
└── 技术源码/            # 可选：Python 命令行引擎 + 测试
    ├── agent/
    │   ├── cli.py          # 命令行入口
    │   ├── models.py       # 数据结构（商品/脚本/分镜/合规问题）
    │   ├── templates.py    # 模板库加载
    │   ├── compliance.py   # 合规校验引擎
    │   ├── generator.py    # 模板模式生成器
    │   ├── llm.py          # LLM 模式生成器
    │   └── exporters.py    # Markdown/JSON/CSV/HTML 导出
    ├── tests/              # unittest 测试（35 个用例）
    └── requirements.txt    # LLM 模式依赖
```

## 六、合规能力说明

- **通用层**：最好/第一/国家级/全网最低 等广告法绝对化用语，一律检测并给出替换建议；
- **医疗品类层**：根治/治愈/药到病除/一贴见效 等功效夸大表述，强校验拦截；
- **自动修正**：可修复表述自动替换（如 一贴见效 → 温和调理），并附加合规提示语（如「本品为日常用品，不能代替药物」）；
- **可测试**：35 个单元测试覆盖模板完整性、合规检测/修正、生成器输出、导出器格式、LLM 提示词与返回解析。

> 说句实话：合规引擎拦的是「已知的高频坑」，不能替代法务意见。真实投放前，还是得以平台最新审核规则和法务确认为准。

## 七、测试

```bash
python -m unittest discover -s tests -v
```

## 八、Roadmap

- [x] 网页版可视化一键出稿（单 HTML，开箱即用）
- [ ] 接入素材库联动（脚本 → 画面提示词 → 出图/出片）
- [ ] 更多行业合规规则包（美妆/食品/服饰）
- [ ] A/B 效果数据回流，自动迭代模板库

---

## English

**E-commerce Viral Script Agent (Qianchuan Ads Edition)** — born from a real internship problem: a content team needed 10+ compliant short-video sales scripts per day. The agent bundles a library of 19 real viral scripts, a five-part template system, and a local compliance engine (China Ad-Law absolute-claim detection + mandatory medical-category checks + auto-rewrite). Ships as a zero-dependency single-HTML web app (double-click to use, no install), plus an optional Python CLI with an LLM mode (OpenAI-compatible API) whose output is still force-checked by the local compliance engine — the model writes, the rules block. 35 unit tests included.

👉 Live demo: <https://jin2004-cmd.github.io/ecom-script-agent/>

---

<div align="center">

如果这个思路对你有用，欢迎 ⭐ **Star** 一下——「模型负责写，规则负责拦」值得被更多做 AI 内容的人看到。

</div>
