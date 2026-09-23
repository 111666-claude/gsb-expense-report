import unittest
from datetime import date

from expense_report.csvio import Expense
from expense_report.filter import (
    FilterError,
    apply_filter,
    build_predicate,
    format_filter_error,
    parse_filter,
)


def expense(text: str = "2026-02-01", category: str = "餐饮", amount: float = 100.0) -> Expense:
    return Expense(day=date.fromisoformat(text), category=category, amount=amount)


class ParseFilterTest(unittest.TestCase):
    def test_amount_operators_with_and_without_spaces(self):
        self.assertEqual(("amount", ">=", 100.0), parse_filter("amount>=100"))
        self.assertEqual(("amount", "<", 5.5), parse_filter("amount < 5.5"))
        self.assertEqual(("amount", "=", 1.0), parse_filter("amount==1"))

    def test_equality_normalized(self):
        self.assertEqual(("amount", "=", 1.0), parse_filter("amount = 1"))
        self.assertEqual(("category", "=", "餐饮"), parse_filter("category==餐饮"))

    def test_category_not_equal(self):
        self.assertEqual(("category", "!=", "交通"), parse_filter("category!=交通"))

    def test_date_value(self):
        column, operator, value = parse_filter("date >= 2026-02-01")
        self.assertEqual(("date", ">="), (column, operator))
        self.assertEqual(date(2026, 2, 1), value)

    def assert_error_offset(self, expression: str, offset: int):
        with self.assertRaises(FilterError) as context:
            parse_filter(expression)
        self.assertEqual(offset, context.exception.offset)
        rendered = format_filter_error(expression, context.exception)
        self.assertIn(str(offset + 1), rendered)
        self.assertIn("^", rendered)

    def test_bad_column_offset(self):
        self.assert_error_offset("amont>=100", 0)

    def test_bad_operator_offset(self):
        self.assert_error_offset("amount>>100", 7)

    def test_missing_value_offset(self):
        self.assert_error_offset("amount>=", 8)

    def test_missing_operator_offset(self):
        self.assert_error_offset("amount 100", 7)

    def test_bad_amount_offset(self):
        self.assert_error_offset("amount=abc", 7)

    def test_bad_date_offset(self):
        self.assert_error_offset("date=2026-13-01", 5)

    def test_category_does_not_support_ordering(self):
        self.assert_error_offset("category>餐饮", 8)

    def test_empty_expression(self):
        self.assert_error_offset("", 0)

    def test_trailing_garbage(self):
        self.assert_error_offset("amount>=100 extra", 11)


class ApplyFilterTest(unittest.TestCase):
    DATA = [
        expense("2026-01-31", "餐饮", 120.5),
        expense("2026-02-01", "交通", 25.0),
        expense("2026-02-03", "购物", 340.0),
    ]

    def test_amount_gte(self):
        rows = apply_filter(self.DATA, "amount>=100")
        self.assertEqual([120.5, 340.0], [item.amount for item in rows])

    def test_category_equals(self):
        rows = apply_filter(self.DATA, "category=餐饮")
        self.assertEqual(["餐饮"], [item.category for item in rows])

    def test_date_comparison(self):
        rows = apply_filter(self.DATA, "date >= 2026-02-01")
        self.assertEqual([25.0, 340.0], [item.amount for item in rows])

    def test_not_equal(self):
        predicate = build_predicate("category!=交通")
        self.assertTrue(predicate(expense(category="餐饮")))
        self.assertFalse(predicate(expense(category="交通")))


if __name__ == "__main__":
    unittest.main()
