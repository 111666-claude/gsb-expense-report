"""读取与校验消费流水 CSV。"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from typing import Iterable

REQUIRED_COLUMNS = ("date", "category", "amount")


class CsvError(ValueError):
    """CSV 内容不合法时抛出。"""


@dataclass(frozen=True)
class Expense:
    """一条流水。"""

    day: date
    category: str
    amount: float


def parse_date(text: str) -> date:
    try:
        return date.fromisoformat(text.strip())
    except ValueError as exc:
        raise CsvError(f"日期格式应为 YYYY-MM-DD：{text!r}") from exc


def parse_row(row: dict[str, str], line_number: int) -> Expense:
    """把一行 CSV 解析成 Expense。"""
    for column in REQUIRED_COLUMNS:
        if column not in row:
            raise CsvError(f"第 {line_number} 行缺少列 {column}")
    category = (row["category"] or "").strip()
    if not category:
        raise CsvError(f"第 {line_number} 行 category 为空")
    raw_amount = (row["amount"] or "").strip()
    try:
        amount = float(raw_amount)
    except ValueError as exc:
        raise CsvError(f"第 {line_number} 行 amount 不是数字：{raw_amount!r}") from exc
    if amount < 0:
        raise CsvError(f"第 {line_number} 行 amount 不能为负数：{raw_amount!r}")
    return Expense(day=parse_date(row["date"]), category=category, amount=amount)


def read_expenses(path: str) -> list[Expense]:
    """读取整个 CSV，返回流水列表。"""
    expenses: list[Expense] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise CsvError("CSV 没有表头")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise CsvError(f"CSV 缺少列：{', '.join(missing)}")
        for number, row in enumerate(reader, start=2):
            expenses.append(parse_row(row, number))
    return expenses


def total_of(expenses: Iterable[Expense]) -> float:
    """流水总金额。"""
    return sum(expense.amount for expense in expenses)
