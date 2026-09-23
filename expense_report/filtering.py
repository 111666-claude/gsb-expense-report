"""解析并执行 ``--filter`` 表达式。

表达式只支持 ``列 比较符 数值`` 一种形式，例如 ``amount>=100``、
``category=餐饮``；列与比较符两侧允许空格。写错时抛出
:class:`FilterError`，报错信息用 ``^`` 指出出错位置。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Sequence

from .csvio import Expense

COLUMNS = ("date", "category", "amount")
EQUALITY_OPERATORS = ("=", "==", "!=")


class FilterError(ValueError):
    """过滤表达式不合法时抛出。"""


def _point(text: str, pos: int, message: str) -> FilterError:
    pos = max(0, min(pos, len(text)))
    return FilterError(f"{message}\n    {text}\n    {' ' * pos}^")


def _skip_spaces(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


@dataclass(frozen=True)
class Filter:
    """一条可执行的过滤条件。"""

    column: str
    operator: str
    value: object
    raw: str

    def matches(self, expense: Expense) -> bool:
        if self.column == "amount":
            left: object = expense.amount
        elif self.column == "date":
            left = expense.day
        else:
            left = expense.category
        right = self.value
        operator = self.operator
        if operator in ("=", "=="):
            return left == right
        if operator == "!=":
            return left != right
        if operator == ">":
            return left > right
        if operator == "<":
            return left < right
        if operator == ">=":
            return left >= right
        return left <= right


def parse_filter(text: str | None) -> Filter:
    """把 ``列 比较符 数值`` 解析成 :class:`Filter`。"""
    text = text or ""
    if not text.strip():
        raise _point(text, 0, "过滤表达式为空，应为 '列 比较符 数值'，例如 amount>=100")

    index = _skip_spaces(text, 0)
    column_start = index
    while (
        index < len(text)
        and not text[index].isspace()
        and text[index] not in "<>=!"
        and not (text[index].isdigit() or text[index] in "+-")
    ):
        index += 1
    column = text[column_start:index]
    if not column:
        raise _point(text, column_start, "缺少列名，应为 date、category 或 amount")
    if column not in COLUMNS:
        raise _point(text, column_start, f"不支持的列 {column!r}，仅支持 date、category、amount")

    operator_start = _skip_spaces(text, index)
    operator = next(
        (
            candidate
            for candidate in (">=", "<=", "==", "!=", ">", "<", "=")
            if text.startswith(candidate, operator_start)
        ),
        None,
    )
    if operator is None:
        symbol = text[operator_start] if operator_start < len(text) else ""
        raise _point(text, operator_start, f"无法识别的比较符 {symbol!r}，支持 >= <= > < = ==")

    next_pos = operator_start + len(operator)
    if next_pos < len(text) and text[next_pos] in "<>=!":
        raise _point(text, operator_start, "无法识别的比较符，支持 >= <= > < = ==")
    value_start = _skip_spaces(text, next_pos)
    if value_start >= len(text):
        raise _point(text, len(text), f"缺少比较值，例如 {column}{operator}100")
    raw_value = text[value_start:].rstrip()

    if column == "amount":
        try:
            value: object = float(raw_value)
        except ValueError as exc:
            raise _point(text, value_start, f"amount 的比较值不是数字：{raw_value!r}") from exc
        if not math.isfinite(value):
            raise _point(text, value_start, f"amount 的比较值应为有限数字：{raw_value!r}")
    elif column == "date":
        try:
            value = date.fromisoformat(raw_value)
        except ValueError as exc:
            raise _point(text, value_start, f"date 的比较值应为 YYYY-MM-DD：{raw_value!r}") from exc
    else:
        if operator not in EQUALITY_OPERATORS:
            raise _point(text, operator_start, "category 是文本列，只支持 =、==、!= 比较")
        value = raw_value

    return Filter(column=column, operator=operator, value=value, raw=text)


def apply_filter(expenses: Sequence[Expense], filter_: Filter | None) -> list[Expense]:
    """返回满足过滤条件的流水（顺序保持不变）；无过滤条件时原样返回。"""
    if filter_ is None:
        return list(expenses)
    return [expense for expense in expenses if filter_.matches(expense)]
