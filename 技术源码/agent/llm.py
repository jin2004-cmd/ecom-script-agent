"""LLM 模式生成器：调用 OpenAI 兼容 Chat API（如火山方舟/豆包）批量生成脚本。"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from .compliance import ComplianceChecker
from .models import Product, Script, Shot
from .templates import TemplateLibrary

DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_MODEL = "doubao-pro-32k"

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


def generate_with_llm(
    product: Product,
    count: int = 5,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 120,
    library: Optional[TemplateLibrary] = None,
    compliance: Optional[ComplianceChecker] = None,
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
        issues = compliance.check(voiceover, medical=product.medical)
        scripts.append(
            Script(
                title=item.get("title", f"方案{index + 1}"),
                hook_type=item.get("hook_type", "LLM 自定义"),
                structure_name=item.get("structure", "LLM 自定义"),
                voiceover=voiceover,
                shots=shots,
                compliance=compliance.summarize(issues),
                meta={"mode": "llm", "index": index + 1},
            )
        )
    return scripts