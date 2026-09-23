"""汇总与表格输出。"""

from __future__ import annotations

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
