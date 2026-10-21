"""LLM 模式生成器：调用 OpenAI 兼容 Chat API（如火山方舟/豆包）批量生成脚本。"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .compliance import ComplianceChecker
from .models import Product, Script, Shot
from .templates import TemplateLibrary

DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_MODEL = "doubao-pro-32k"


# LLM 模式要求模型直接返回 JSON（response_format=json_object），
# 这里把期望结构写清楚，避免模型自由发挥导致解析失败。
OUTPUT_SCHEMA = """{
  "scripts": [
    {
      "title": "方案标题",
      "hook_type": "钩子类型名（必须是可用钩子之一）",
      "structure": "结构名（必须是可用结构之一）",
      "voiceover": "完整口播文案，纯文本，用换行分段",
      "shots": [
        {
          "time_range": "0-3s",
          "scene": "画面描述",
          "subtitle": "字幕文案",
          "voiceover": "该分镜对应的口播"
        }
      ]
    }
  ]
}"""


def _load_env_file(path: str | None = None) -> None:
    """读取项目根目录的 .env（纯标准库实现，真实环境变量优先）。"""
    env_path = Path(path) if path else (Path(__file__).resolve().parent.parent / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip(chr(34) + chr(39)))


def _build_system_prompt(library: TemplateLibrary) -> str:
    """构建系统提示词：角色、输出格式、合规红线、可用钩子与结构。

    说明：本函数在 v1.0.4 之前被 generate_with_llm 调用但从未定义，
    LLM 模式一旦执行就会抛 NameError。此处为补全实现。
    """
    hook_names = library.hook_names()
    structure_names = library.structure_names()
    return "\n".join([
        "你是资深电商短视频脚本策划，负责为千川投放场景产出可直接拍摄的带货口播脚本。",
        "",
        "【输出格式】",
        "只输出一个 JSON 对象，不要任何解释文字，不要 Markdown 代码块围栏。结构如下：",
        OUTPUT_SCHEMA,
        "",
        "【合规红线】",
        "1. 禁止《广告法》绝对化用语：最、第一、顶级、国家级、最佳、唯一、绝无仅有等。",
        "2. 禁止夸大功效与虚假承诺：根治、包治、永不反弹、百分百有效、彻底治愈等。",
        "3. 禁止医疗化表述：治疗、疗效、药效、处方等（非医疗资质商品一律不得出现）。",
        "4. 不得虚构数据、排名、资质、检测报告或用户见证。",
        "",
        "【可用钩子类型】",
        "、".join(hook_names) or "（模板库为空）",
        "",
        "【可用结构】",
        "、".join(structure_names) or "（模板库为空）",
        "",
        "【写作要求】",
        "1. 前 3 秒必须给出强钩子，直接打痛点或制造反差。",
        "2. 口播口语化，短句为主，单句不超过 25 字，总时长控制在 30-45 秒。",
        "3. shots 的数量与所选结构的段落数一致，各分镜 voiceover 拼接后应覆盖完整口播。",
        "4. hook_type 与 structure 两个字段必须原样使用上面列出的名称。",
    ])


def _build_user_prompt(product: Product, count: int, library: TemplateLibrary) -> str:
    """构建用户提示词：商品信息 + 生成数量 + 差异化要求。"""
    lines = [
        "请为下面的商品生成 %d 条互不相同的带货脚本。" % count,
        "",
        "【商品信息】",
        "名称：%s" % product.name,
        "类目：%s" % product.category,
        "价格：%s 元" % product.price,
        "卖点：%s" % ("、".join(product.selling_points) or "未提供，请按类目常识提炼"),
        "痛点：%s" % ("、".join(product.pain_points) or "未提供，请按类目常识提炼"),
        "目标人群：%s" % product.target_audience,
    ]
    if product.brand:
        lines.append("品牌：%s" % product.brand)
    if product.trust_proof:
        lines.append("信任背书：%s" % product.trust_proof)
    if product.promo:
        lines.append("优惠信息：%s" % product.promo)
    if product.medical:
        lines.append("【特别提醒】该商品属医疗/健康类目，不得出现功效承诺与治疗性表述。")
    lines += [
        "",
        "【要求】",
        "1. 每条使用不同的钩子类型，并尽量覆盖不同的结构。",
        "2. shots 的数量与所选结构的段落数一致。",
        "3. 只返回 JSON 对象，不要附加任何说明。",
    ]
    return "\n".join(lines)


def _parse_scripts(
    parsed: Dict,
    product: Product,
    compliance: ComplianceChecker,
    auto_fix: bool,
) -> List[Script]:
    """把模型返回的 JSON 解析成 Script 列表，并统一过一遍合规引擎。"""
    scripts: List[Script] = []
    for index, item in enumerate(parsed.get("scripts", [])):
        shots = [
            Shot(
                time_range=shot.get("time_range", ""),
                scene=shot.get("scene", ""),
                subtitle=shot.get("subtitle", ""),
                voiceover=shot.get("voiceover", ""),
            )
            for shot in item.get("shots", [])
        ]

        voiceover = item.get("voiceover", "")
        if auto_fix:
            voiceover, remaining, replaced = compliance.fix(voiceover, medical=product.medical)
        else:
            remaining = compliance.check(voiceover, medical=product.medical)
            replaced = []

        disclaimers = compliance.disclaimers(medical=product.medical)
        if disclaimers:
            voiceover += "\n\n" + "\n".join("（合规提示）" + line for line in disclaimers)

        scripts.append(
            Script(
                title=item.get("title", f"方案{index + 1}"),
                hook_type=item.get("hook_type", "LLM 自定义"),
                structure_name=item.get("structure", "LLM 自定义"),
                voiceover=voiceover,
                shots=shots,
                compliance=compliance.summarize(remaining),
                meta={
                    "mode": "llm",
                    "index": index + 1,
                    "disclaimers": disclaimers,
                    "replaced": [{"word": w, "to": r} for w, r in replaced],
                },
            )
        )
    return scripts


def generate_with_llm(
    product: Product,
    count: int = 5,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 120,
    library: Optional[TemplateLibrary] = None,
    compliance: Optional[ComplianceChecker] = None,
    auto_fix: bool = True,
) -> List[Script]:
    """通过 LLM 生成脚本，生成后仍会过一遍合规引擎。"""
    try:
        import requests  # noqa: PLC0415
    except ImportError:
        raise RuntimeError("LLM 模式需要 requests 库，请先执行: pip install -r requirements.txt")

    library = library or TemplateLibrary()
    compliance = compliance or ComplianceChecker()

    _load_env_file()

    api_key = api_key or os.getenv("ARK_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 API Key：请设置环境变量 ARK_API_KEY 或传入 --api-key")
    base_url = (base_url or os.getenv("ARK_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    model = model or os.getenv("ARK_MODEL") or DEFAULT_MODEL

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _build_system_prompt(library)},
            {"role": "user", "content": _build_user_prompt(product, count, library)},
        ],
        "temperature": 0.9,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    response = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)

    return _parse_scripts(parsed, product, compliance, auto_fix)
