"""命令行入口。

用法：
    python3 -m expense_report.cli --file sample/expenses.csv
"""

from __future__ import annotations

import argparse
from typing import Sequence

from .csvio import CsvError, read_expenses
from .report import format_report, group_by_day


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expense-report", description="消费流水汇总")
    parser.add_argument("--file", required=True, help="消费流水 CSV 路径")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        expenses = read_expenses(args.file)
    except CsvError as exc:
        print(f"读取失败：{exc}")
        return 2
    print(format_report(group_by_day(expenses)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
