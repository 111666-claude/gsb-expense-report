"""汇总与表格输出。"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Sequence

from .csvio import Expense

DEFAULT_WEEK_YEAR = 2026


def group_by_day(expenses: Sequence[Expense]) -> list[tuple[date, float]]:
    """按天汇总，返回按日期升序排列的 (日期, 金额)。"""
    totals: dict[date, float] = defaultdict(float)
    for expense in expenses:
        totals[expense.day] += expense.amount
    return sorted(totals.items(), key=lambda item: item[0])


def week_label(day: date) -> str:
    """返回 ISO 周标签，周一起算；2026 ISO 年用 ``W05``，其余带年份。"""
    iso_year, iso_week, _ = day.isocalendar()
    if iso_year == DEFAULT_WEEK_YEAR:
        return f"W{iso_week:02d}"
    return f"{iso_year}-W{iso_week:02d}"


def group_by_week(expenses: Sequence[Expense]) -> list[tuple[str, float]]:
    """按 ISO 周（周一起算）汇总，返回按时间升序排列的 (周标签, 金额)。"""
    totals: dict[tuple[int, int], float] = defaultdict(float)
    for expense in expenses:
        iso_year, iso_week, _ = expense.day.isocalendar()
        totals[(iso_year, iso_week)] += expense.amount
    return [(week_label(date.fromisocalendar(iso_year, iso_week, 1)), total)
            for (iso_year, iso_week), total in sorted(totals.items())]


def group_by_month(expenses: Sequence[Expense]) -> list[tuple[str, float]]:
    """按月汇总，返回按时间升序排列的 (``YYYY-MM``, 金额)。"""
    totals: dict[tuple[int, int], float] = defaultdict(float)
    for expense in expenses:
        totals[(expense.day.year, expense.day.month)] += expense.amount
    return [(f"{year:04d}-{month:02d}", total)
            for (year, month), total in sorted(totals.items())]


def format_amount(value: float) -> str:
    return f"{value:.2f}"


def format_report(rows: Sequence[tuple[object, float]], title: str = "日期") -> str:
    """把 (分组标签, 金额) 列表渲染成文本报表。"""
    lines = [f"{title}        金额", "-" * 20]
    for label, total in rows:
        text = label.isoformat() if isinstance(label, date) else str(label)
        lines.append(f"{text}  {format_amount(total):>8}")
    lines.append("-" * 20)
    lines.append(f"合计        {format_amount(sum(total for _, total in rows)):>8}")
    return "\n".join(lines)


def top_categories(expenses: Sequence[Expense], limit: int) -> list[tuple[str, float, float]]:
    """按类别汇总，返回金额最高的若干类别。

    每项为 (类别, 金额, 占总计的百分比)。金额降序，金额相同时按类别名
    升序，保证输出稳定。``limit`` 小于类别总数时截断。
    """
    totals: dict[str, float] = defaultdict(float)
    for expense in expenses:
        totals[expense.category] += expense.amount
    grand_total = sum(totals.values())
    ordered = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    if limit < len(ordered):
        ordered = ordered[:limit]
    percent = (lambda amount: amount / grand_total * 100.0) if grand_total else (lambda amount: 0.0)
    return [(category, amount, percent(amount)) for category, amount in ordered]


def format_top(rows: Sequence[tuple[str, float, float]], grand_total: float) -> str:
    """把 (类别, 金额, 占比) 列表渲染成文本报表。"""
    lines = ["类别          金额    占比", "-" * 26]
    for category, amount, percentage in rows:
        lines.append(f"{category}      {format_amount(amount):>8}  {percentage:5.1f}%")
    lines.append("-" * 26)
    lines.append(f"合计      {format_amount(grand_total):>8}  100.0%")
    return "\n".join(lines)
