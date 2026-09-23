"""汇总与表格输出。"""

from __future__ import annotations

import unicodedata
from collections import defaultdict
from datetime import date
from typing import Sequence

from .csvio import Expense


def group_by_day(expenses: Sequence[Expense]) -> list[tuple[date, float]]:
    """按天汇总，返回按日期升序排列的 (日期, 金额)。"""
    totals: dict[date, float] = defaultdict(float)
    for expense in expenses:
        totals[expense.day] += expense.amount
    return sorted(totals.items(), key=lambda item: item[0])


def group_by_week(expenses: Sequence[Expense]) -> list[tuple[str, float]]:
    """按 ISO 周（周一起算）汇总，返回按时间升序的 (周标签, 金额)。

    标签形如 ``2026-W05``；跨年时以 ISO 周年为准排序。
    """
    totals: dict[tuple[int, int], float] = defaultdict(float)
    for expense in expenses:
        iso = expense.day.isocalendar()
        totals[(iso.year, iso.week)] += expense.amount
    ordered = sorted(totals.items(), key=lambda item: item[0])
    return [
        (f"{iso_year}-W{iso_week:02d}", total)
        for (iso_year, iso_week), total in ordered
    ]


def group_by_month(expenses: Sequence[Expense]) -> list[tuple[str, float]]:
    """按月汇总，返回按时间升序的 (月份标签, 金额)，标签形如 ``2026-02``。"""
    totals: dict[tuple[int, int], float] = defaultdict(float)
    for expense in expenses:
        totals[(expense.day.year, expense.day.month)] += expense.amount
    ordered = sorted(totals.items(), key=lambda item: item[0])
    return [
        (f"{year:04d}-{month:02d}", total)
        for (year, month), total in ordered
    ]


def top_categories(
    expenses: Sequence[Expense], limit: int
) -> list[tuple[str, float]]:
    """返回金额最高的 limit 个 (类别, 金额)；金额相同按类别名升序。"""
    totals: dict[str, float] = defaultdict(float)
    for expense in expenses:
        totals[expense.category] += expense.amount
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:limit]


def format_amount(value: float) -> str:
    return f"{value:.2f}"


def format_report(rows: Sequence[tuple[date, float]]) -> str:
    """把 (日期, 金额) 列表渲染成文本报表。"""
    lines = ["日期        金额", "-" * 20]
    for day, total in rows:
        lines.append(f"{day.isoformat()}  {format_amount(total):>8}")
    lines.append("-" * 20)
    lines.append(f"合计        {format_amount(sum(total for _, total in rows)):>8}")
    return "\n".join(lines)


def _display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def _pad(text: str, width: int) -> str:
    return text + " " * max(0, width - _display_width(text))


def format_labeled_report(title: str, rows: Sequence[tuple[str, float]]) -> str:
    """渲染 (文本标签, 金额) 的周/月报表。"""
    lines = [f"{_pad(title, 8)}  金额", "-" * 20]
    for label, total in rows:
        lines.append(f"{_pad(label, 8)}  {format_amount(total):>8}")
    lines.append("-" * 20)
    lines.append(f"{_pad('合计', 8)}  {format_amount(sum(total for _, total in rows)):>8}")
    return "\n".join(lines)


def format_week_report(rows: Sequence[tuple[str, float]]) -> str:
    """渲染 ISO 周报表。"""
    return format_labeled_report("周", rows)


def format_month_report(rows: Sequence[tuple[str, float]]) -> str:
    """渲染月报表。"""
    return format_labeled_report("月份", rows)


def format_percent(part: float, whole: float) -> str:
    """金额占比，保留一位小数；总额为 0 时显示 0.0%。"""
    if whole == 0:
        return "0.0%"
    return f"{part / whole * 100:.1f}%"


def format_top_report(
    rows: Sequence[tuple[str, float]], grand_total: float
) -> str:
    """渲染类别金额 Top N 报表，占比分母为全部流水总额。"""
    lines = ["类别      金额        占比", "-" * 26]
    shown = 0.0
    for category, total in rows:
        lines.append(
            f"{_pad(category, 8)}  {format_amount(total):>8}  {format_percent(total, grand_total):>6}"
        )
        shown += total
    lines.append("-" * 26)
    lines.append(
        f"{_pad('合计', 8)}  {format_amount(shown):>8}  {format_percent(shown, grand_total):>6}"
    )
    return "\n".join(lines)
