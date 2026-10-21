"""命令行入口：生成脚本、合规检测、模板查看、示例演示。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .compliance import ComplianceChecker
from .exporters import export_all
from .generator import ScriptGenerator
from .llm import generate_with_llm
from .models import Product
from .templates import TemplateLibrary

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def _load_products() -> List[Product]:
    with open(DATA_DIR / "products.json", encoding="utf-8-sig") as f:
        items = json.load(f)
    return [Product(**item) for item in items]


def _print_scripts_summary(scripts) -> None:
    print(f"共生成 {len(scripts)} 条脚本：")
    for script in scripts:
        status = "通过" if script.compliance["passed"] else f"{script.compliance['issue_count']} 个问题"
        print(f"  - {script.title} ｜ 合规：{status}")


def cmd_generate(args: argparse.Namespace) -> int:
    product = Product(
        name=args.product,
        category=args.category,
        price=args.price,
        selling_points=args.points,
        pain_points=args.pains,
        target_audience=args.audience,
        brand=args.brand,
        trust_proof=args.trust,
        promo=args.promo,
        medical=args.medical,
    )
    if args.mode == "template":
        generator = ScriptGenerator()
        scripts = generator.generate(product, count=args.count, seed=args.seed, auto_fix=not args.no_fix)
    else:
        scripts = generate_with_llm(
            product,
            count=args.count,
            api_key=args.api_key,
            base_url=args.base_url,
            model=args.model,
            auto_fix=not args.no_fix,
        )
    out_dir = Path(args.out)
    formats = tuple(f.strip() for f in args.formats.split(",") if f.strip())
    saved = export_all(scripts, out_dir, prefix=args.prefix, formats=formats)
    _print_scripts_summary(scripts)
    print("\n已导出：")
    for path in saved:
        print(f"  - {path}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    products = _load_products()
    generator = ScriptGenerator()
    out_dir = ROOT / "examples" / "demo"
    for product in products:
        scripts = generator.generate(product, count=args.count, seed=args.seed, auto_fix=True)
        export_all(scripts, out_dir, prefix=product.name, formats=("md", "json", "csv", "html"))
        _print_scripts_summary(scripts)
        print()
    print(f"示例已导出到：{out_dir}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    checker = ComplianceChecker()
    issues = checker.check(args.text, medical=args.medical)
    if not issues:
        print("✅ 合规检查通过（0 个问题）")
        return 0
    print(f"⚠️ 发现 {len(issues)} 个问题：")
    for issue in issues:
        print(f"  - [{issue.severity}] 「{issue.word}」｜{issue.message}｜建议：{issue.suggestion}")
    return 1


def cmd_templates(args: argparse.Namespace) -> int:
    library = TemplateLibrary()
    print("== 黄金3秒钩子模板 ==")
    for hook in library.hooks:
        print(f"  [{hook['id']}] {hook['name']}：{hook['template']}")
    print("\n== 脚本结构模板 ==")
    for structure in library.structures:
        sections = " → ".join(section["name"] for section in structure["sections"])
        print(f"  [{structure['id']}] {structure['name']}：{sections}")
    print("\n== CTA 转化话术 ==")
    for cta in library.ctas:
        print(f"  [{cta['id']}] {cta['name']}：{cta['template']}")
    return 0


def cmd_products(args: argparse.Namespace) -> int:
    for index, product in enumerate(_load_products(), start=1):
        print(f"{index}. {product.name}（{product.category}，¥{product.price}）medical={product.medical}")
        print(f"   卖点：{'、'.join(product.selling_points)}")
        print(f"   痛点：{'、'.join(product.pain_points)}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="脚本生成智能体",
        description="电商短视频爆款脚本生成智能体（千川带货版）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate", help="根据商品信息生成带货脚本")
    generate.add_argument("--product", required=True, help="商品名称")
    generate.add_argument("--category", default="general", help="商品品类，如 医疗保健/3C数码")
    generate.add_argument("--price", type=float, default=39.9, help="售价")
    generate.add_argument("--points", action="append", default=[], help="卖点（可多次传入）")
    generate.add_argument("--pains", action="append", default=[], help="痛点（可多次传入）")
    generate.add_argument("--audience", default="目标人群", help="目标人群")
    generate.add_argument("--brand", default="", help="品牌名")
    generate.add_argument("--trust", default="", help="信任背书")
    generate.add_argument("--promo", default="", help="促销信息，如：第二件半价")
    generate.add_argument("--medical", action="store_true", help="医疗相关品类，启用强合规校验")
    generate.add_argument("--count", type=int, default=5, help="生成脚本数量（默认 5）")
    generate.add_argument("--seed", type=int, default=None, help="随机种子，保证可复现")
    generate.add_argument("--mode", choices=["template", "llm"], default="template", help="生成模式")
    generate.add_argument("--api-key", default=None, help="LLM 模式 API Key（或设置 ARK_API_KEY）")
    generate.add_argument("--base-url", default=None, help="LLM 模式 Base URL（默认火山方舟）")
    generate.add_argument("--model", default=None, help="LLM 模式模型名")
    generate.add_argument("--out", default="examples/generated", help="输出目录")
    generate.add_argument("--prefix", default="script", help="输出文件前缀")
    generate.add_argument("--formats", default="md,json,csv,html", help="导出格式，逗号分隔")
    generate.add_argument("--no-fix", action="store_true", help="关闭自动合规修正（只检测不替换）")
    generate.set_defaults(func=cmd_generate)

    demo = sub.add_parser("demo", help="跑通内置示例商品（肠胃贴 + 蓝牙耳机）")
    demo.add_argument("--count", type=int, default=5, help="每个商品生成数量")
    demo.add_argument("--seed", type=int, default=42, help="随机种子")
    demo.set_defaults(func=cmd_demo)

    check = sub.add_parser("check", help="合规检测一段文案")
    check.add_argument("--text", required=True, help="待检测文案")
    check.add_argument("--medical", action="store_true", help="按医疗品类强校验")
    check.set_defaults(func=cmd_check)

    templates = sub.add_parser("templates", help="查看内置爆款结构模板库")
    templates.set_defaults(func=cmd_templates)

    products = sub.add_parser("products", help="查看内置示例商品")
    products.set_defaults(func=cmd_products)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())