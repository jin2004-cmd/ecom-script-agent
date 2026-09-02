"""多格式导出：Markdown / JSON / CSV / HTML。"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Iterable, List, Optional

from .models import Script


def script_to_markdown(script: Script) -> str:
    compliance = script.compliance
    head = f"""# {script.title}

- 结构：{script.structure_name}
- 钩子：{script.hook_type}
- 模式：{script.meta.get("mode", "template")}

## 口播文案

{script.voiceover}

## 分镜脚本

| 时间 | 画面 | 字幕 | 口播 |
| --- | --- | --- | --- |
"""
    rows = "\n".join(
        f"| {shot.time_range} | {shot.scene} | {shot.subtitle} | {shot.voiceover} |"
        for shot in script.shots
    )
    if compliance["passed"]:
        compliance_text = "✅ 通过（0 个问题）"
    else:
        lines = [f"⚠️ {compliance['issue_count']} 个问题："]
        lines += [
            f"- [{issue['severity']}] {issue['word']}｜{issue['message']}｜建议：{issue['suggestion']}"
            for issue in compliance["issues"]
        ]
        compliance_text = "\n".join(lines)
    tail = f"""
## 合规结果

{compliance_text}
"""
    disclaimers = compliance.get("disclaimers") or []
    if disclaimers:
        tail += "\n## 合规提示\n\n" + "\n".join(f"- {line}" for line in disclaimers) + "\n"
    replaced = script.meta.get("replaced") or []
    if replaced:
        tail += "\n## 自动修正记录\n\n" + "\n".join(f"- {item['word']} → {item['to']}" for item in replaced) + "\n"
    return head + rows + tail


def scripts_to_csv(scripts: Iterable[Script]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["title", "hook_type", "structure_name", "voiceover", "compliance_passed", "issue_count", "time_ranges", "scenes"]
    )
    for script in scripts:
        writer.writerow(
            [
                script.title,
                script.hook_type,
                script.structure_name,
                script.voiceover.replace("\n", " / "),
                script.compliance["passed"],
                script.compliance["issue_count"],
                " | ".join(shot.time_range for shot in script.shots),
                " | ".join(shot.scene for shot in script.shots),
            ]
        )
    return buffer.getvalue()


def scripts_to_json(scripts: Iterable[Script]) -> dict:
    return {"scripts": [script.to_dict() for script in scripts]}


def scripts_to_html(scripts: Iterable[Script]) -> str:
    blocks = []
    for script in scripts:
        status = "✅ 通过" if script.compliance["passed"] else f"⚠️ {script.compliance['issue_count']} 个问题"
        voiceover_html = "".join(f"<p>{line}</p>" for line in script.voiceover.split("\n") if line.strip())
        shots_rows = "".join(
            f"<tr><td>{shot.time_range}</td><td>{shot.scene}</td><td>{shot.subtitle}</td><td>{shot.voiceover}</td></tr>"
            for shot in script.shots
        )
        blocks.append(
            f"""<section class="script">
<h2>{script.title}</h2>
<p class="meta">{script.structure_name} ｜ {script.hook_type} ｜ 模式：{script.meta.get('mode', 'template')}</p>
<div class="status">{status}</div>
<h3>口播文案</h3>
<div class="voiceover">{voiceover_html}</div>
<h3>分镜脚本</h3>
<table><tr><th>时间</th><th>画面</th><th>字幕</th><th>口播</th></tr>{shots_rows}</table>
</section>"""
        )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>电商短视频爆款脚本生成智能体 - 示例输出</title>
<style>
body {{ font-family: "Microsoft YaHei", sans-serif; max-width: 960px; margin: 24px auto; padding: 0 16px; color: #222; }}
h1 {{ border-bottom: 2px solid #333; padding-bottom: 8px; }}
.script {{ border: 1px solid #ddd; border-radius: 8px; padding: 16px 20px; margin: 20px 0; }}
.meta {{ color: #666; }}
.status {{ display: inline-block; padding: 2px 10px; border-radius: 4px; background: #e8f5e9; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 6px 8px; font-size: 13px; vertical-align: top; }}
th {{ background: #f5f5f5; }}
.voiceover p {{ margin: 4px 0; }}
</style>
</head>
<body>
<h1>电商短视频爆款脚本生成智能体 · 示例输出</h1>
{''.join(blocks)}
</body>
</html>"""


def export_all(
    scripts: Iterable[Script],
    out_dir: Path,
    prefix: str = "script",
    formats: Iterable[str] = ("md", "json", "csv", "html"),
) -> List[Path]:
    """按指定格式导出脚本集，返回生成的文件路径列表。"""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    script_list = list(scripts)
    saved: List[Path] = []
    for fmt in formats:
        if fmt == "md":
            path = out_dir / f"{prefix}.md"
            content = "\n\n---\n\n".join(script_to_markdown(s) for s in script_list)
        elif fmt == "json":
            path = out_dir / f"{prefix}.json"
            content = json.dumps(scripts_to_json(script_list), ensure_ascii=False, indent=2)
        elif fmt == "csv":
            path = out_dir / f"{prefix}.csv"
            content = scripts_to_csv(script_list)
        elif fmt == "html":
            path = out_dir / f"{prefix}.html"
            content = scripts_to_html(script_list)
        else:
            continue
        path.write_text(content, encoding="utf-8")
        saved.append(path)
    return saved