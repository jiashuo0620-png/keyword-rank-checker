"""命令行入口：读取关键词表 → 批量检索 → 导出 Excel。"""

import argparse
import csv
from pathlib import Path

from src.checker import check_all
from src.export import export_excel
from src.providers.duckduckgo import DuckDuckGoProvider
from src.providers.mock import MockProvider

BASE_DIR = Path(__file__).resolve().parent


def load_pairs(csv_path: str) -> list[tuple[str, str]]:
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [
            (row["keyword"].strip(), row["domain"].strip())
            for row in reader
            if row.get("keyword") and row.get("domain")
        ]


def build_provider(name: str):
    if name == "mock":
        return MockProvider(BASE_DIR / "data" / "fixtures.json")
    if name == "duckduckgo":
        return DuckDuckGoProvider()
    raise ValueError(f"未知检索源: {name}")


def parse_args():
    parser = argparse.ArgumentParser(description="关键词收录与排名批量检查")
    parser.add_argument("--input", required=True, help="关键词 CSV 路径")
    parser.add_argument(
        "--provider", default="mock", choices=["mock", "duckduckgo"], help="检索源"
    )
    parser.add_argument("--output", default="outputs/report.xlsx", help="Excel 输出路径")
    parser.add_argument("--limit", type=int, default=10, help="每词检查前 N 条结果")
    parser.add_argument("--concurrency", type=int, default=4, help="并发线程数")
    parser.add_argument("--delay", type=float, default=0.5, help="请求间隔（秒）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pairs = load_pairs(args.input)
    if not pairs:
        print("输入为空，请检查 CSV 格式：keyword,domain")
        return 1

    provider = build_provider(args.provider)
    print(f"开始检查 {len(pairs)} 个关键词（检索源: {provider.name}）...")

    results = check_all(
        provider,
        pairs,
        limit=args.limit,
        concurrency=args.concurrency,
        delay=args.delay,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    export_excel(results, str(output))

    found = sum(1 for item in results if item.found)
    errors = sum(1 for item in results if item.status == "error")
    print(f"完成: {found}/{len(results)} 命中，{errors} 个出错")
    print(f"报告已导出: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
