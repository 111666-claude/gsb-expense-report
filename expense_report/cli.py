"""命令行入口。

用法：
    python3 -m expense_report.cli --file sample/expenses.csv
"""

from __future__ import annotations

import argparse
from typing import Sequence

from .csvio import CsvError, read_expenses, total_of
from .filter import FilterError, apply_filter, format_filter_error
from .report import (
    format_month_report,
    format_report,
    format_top_report,
    format_week_report,
    group_by_day,
    group_by_month,
    group_by_week,
    top_categories,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expense-report", description="消费流水汇总")
    parser.add_argument("--file", required=True, help="消费流水 CSV 路径")
    parser.add_argument(
        "--group-by",
        default="day",
        help="汇总粒度：day（按天，默认）、week（按 ISO 周）、month（按月）",
    )
    parser.add_argument("--top", default=None, help="输出金额最高的 N 个类别")
    parser.add_argument(
        "--filter",
        dest="condition",
        default=None,
        help="只统计满足条件的记录，例如 amount>=100、category=餐饮",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.group_by not in ("day", "week", "month"):
        print(f"参数错误：--group-by 只能是 day、week、month，收到 {args.group_by!r}")
        return 2
    top_limit: int | None = None
    if args.top is not None:
        try:
            top_limit = int(args.top)
        except ValueError:
            top_limit = 0
        if top_limit < 1:
            print(f"参数错误：--top 必须是正整数，收到 {args.top!r}")
            return 2
    if top_limit is not None and args.group_by != "day":
        print("参数错误：--top 不能与 --group-by week/month 同时使用")
        return 2
    try:
        expenses = read_expenses(args.file)
    except CsvError as exc:
        print(f"读取失败：{exc}")
        return 2
    if args.condition is not None:
        try:
            expenses = apply_filter(expenses, args.condition)
        except FilterError as exc:
            print(format_filter_error(args.condition, exc))
            return 2
    if top_limit is not None:
        print(format_top_report(top_categories(expenses, top_limit), total_of(expenses)))
        return 0
    if args.group_by == "week":
        print(format_week_report(group_by_week(expenses)))
    elif args.group_by == "month":
        print(format_month_report(group_by_month(expenses)))
    else:
        print(format_report(group_by_day(expenses)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
