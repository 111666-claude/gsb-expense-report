"""解析并应用 ``--filter '列 比较符 数值'`` 表达式。"""

from __future__ import annotations

import math
import re
from datetime import date
from typing import Callable, Sequence

from .csvio import Expense

COLUMNS = ("date", "category", "amount")
NUMERIC_OPS = (">=", "<=", "==", "!=", ">", "<", "=")
TEXT_OPS = ("=", "==", "!=")
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class FilterError(ValueError):
    """过滤表达式不合法时抛出，offset 指向表达式中的出错位置（0 起算）。"""

    def __init__(self, message: str, offset: int):
        super().__init__(message)
        self.message = message
        self.offset = offset


def _skip_spaces(text: str, index: int) -> int:
    while index < len(text) and text[index] == " ":
        index += 1
    return index


def _read_column(text: str, start: int) -> tuple[str, int]:
    end = start
    while end < len(text) and (text[end].isalpha() or text[end] == "_"):
        end += 1
    name = text[start:end]
    if not name:
        raise FilterError("应以列名开头，可选 date、category、amount", start)
    if name not in COLUMNS:
        raise FilterError(
            f"不支持的列 {name!r}，可选 date、category、amount", start
        )
    return name, end


def _read_operator(text: str, start: int, column: str) -> tuple[str, int]:
    if start >= len(text):
        raise FilterError("缺少比较符，可选 >=、<=、==、!=、>、<、=", start)
    ops = TEXT_OPS if column == "category" else NUMERIC_OPS
    for length in (2, 1):
        candidate = text[start:start + length]
        if candidate in ops:
            return candidate, start + length
    raise FilterError(f"比较符应为 {'、'.join(ops)}", start)


def _parse_amount(raw: str, offset: int) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise FilterError(f"金额应为数字：{raw!r}", offset) from exc
    if not math.isfinite(value):
        raise FilterError(f"金额应为有限数字：{raw!r}", offset)
    return value


def _parse_date(raw: str, offset: int) -> date:
    if not DATE_RE.match(raw):
        raise FilterError(f"日期应为 YYYY-MM-DD：{raw!r}", offset)
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise FilterError(f"日期不是有效日期：{raw!r}", offset) from exc


def parse_filter(expression: str) -> tuple[str, str, object]:
    """解析 ``列 比较符 值``，返回 (列名, 规范比较符, 解析后的值)。"""
    index = _skip_spaces(expression, 0)
    if index >= len(expression):
        raise FilterError("表达式不能为空，例如 amount>=100", 0)
    column, index = _read_column(expression, index)
    index = _skip_spaces(expression, index)
    operator, index = _read_operator(expression, index, column)
    index = _skip_spaces(expression, index)
    if index >= len(expression):
        raise FilterError("比较符后缺少数值", index)
    end = len(expression.rstrip(" "))
    raw = expression[index:end]
    if " " in raw:
        space = index + raw.index(" ")
        raise FilterError("数值中间不能出现空格", space)
    if column == "amount":
        value: object = _parse_amount(raw, index)
    elif column == "date":
        value = _parse_date(raw, index)
    else:
        value = raw
    return column, ("=" if operator == "==" else operator), value


def _compare(left: object, operator: str, right: object) -> bool:
    if operator == "=":
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


def build_predicate(expression: str) -> Callable[[Expense], bool]:
    """把表达式编译成针对 Expense 的判定函数。"""
    column, operator, value = parse_filter(expression)
    if column == "category":
        return lambda item: _compare(item.category, operator, value)
    if column == "amount":
        return lambda item: _compare(item.amount, operator, value)
    return lambda item: _compare(item.day, operator, value)


def apply_filter(
    expenses: Sequence[Expense], expression: str
) -> list[Expense]:
    """返回满足表达式的流水。"""
    predicate = build_predicate(expression)
    return [item for item in expenses if predicate(item)]


def _visual_column(text: str) -> int:
    import unicodedata

    return sum(
        2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text
    )


def format_filter_error(expression: str, error: FilterError) -> str:
    """渲染带位置指示的错误信息（按终端显示列对齐中文等宽字符）。"""
    offset = min(error.offset, len(expression))
    caret = " " * _visual_column(expression[:offset]) + "^"
    return f"过滤条件有误（第 {offset + 1} 个字符）：{error.message}\n  {expression}\n  {caret}"
