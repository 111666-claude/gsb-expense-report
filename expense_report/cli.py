"""命令行入口。

用法：
    python3 -m expense_report.cli --file sample/expenses.csv
    python3 -m expense_report.cli --file sample/expenses.csv --group-by week
    python3 -m expense_report.cli --file sample/expenses.csv --top 2
    python3 -m expense_report.cli --file sample/expenses.csv --filter 'amount>=100'
"""

from __future__ import annotations

import argparse
from typing import Sequence

from .csvio import CsvError, read_expenses
from .filtering import FilterError, apply_filter, parse_filter
from .report import (
    format_report,
    format_top,
    group_by_day,
    group_by_month,
    group_by_week,
    top_categories,
)

GROUPS = {
    "day": ("日期", group_by_day),
    "week": ("周", group_by_week),
    "month": ("月份", group_by_month),
}


def positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"应为正整数：{text!r}") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError(f"应为正整数：{text!r}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expense-report", description="消费流水汇总")
    parser.add_argument("--file", required=True, help="消费流水 CSV 路径")
    parser.add_argument(
        "--group-by",
        choices=("day", "week", "month"),
        default="day",
        help="汇总粒度：day 按天（默认）、week 按 ISO 周（周一起算）、month 按月",
    )
    parser.add_argument("--top", type=positive_int, default=None, metavar="N", help="输出金额最高的 N 个类别及占比")
    parser.add_argument("--filter", dest="filter_expr", default=None, metavar="表达式",
                        help="只统计满足条件的记录，例如 amount>=100、category=餐饮")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.top is not None and args.group_by != "day":
        print("参数冲突：--top 不能与 --group-by week|month 同时使用（类别 top 已按全部时间汇总）")
        return 2

    filter_ = None
    if args.filter_expr is not None:
        try:
            filter_ = parse_filter(args.filter_expr)
        except FilterError as exc:
            print(f"过滤表达式有误：\n{exc}")
            return 2

    try:
        expenses = read_expenses(args.file)
    except CsvError as exc:
        print(f"读取失败：{exc}")
        return 2

    expenses = apply_filter(expenses, filter_)

    if args.top is not None:
        print(format_top(top_categories(expenses, args.top), sum(expense.amount for expense in expenses)))
    else:
        title, grouper = GROUPS[args.group_by]
        print(format_report(grouper(expenses), title=title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
