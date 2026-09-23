import unittest
from datetime import date

from expense_report.csvio import Expense
from expense_report.filtering import FilterError, apply_filter, parse_filter


def expense(day: str = "2026-02-01", category: str = "餐饮", amount: float = 100.0) -> Expense:
    year, month, day_of_month = (int(part) for part in day.split("-"))
    return Expense(day=date(year, month, day_of_month), category=category, amount=amount)


def caret_column(message: str) -> int:
    pointer_line = message.splitlines()[-1]
    return pointer_line.index("^") - len("    ")


class ParseFilterTest(unittest.TestCase):
    def test_amount_comparisons(self):
        self.assertTrue(parse_filter("amount>=100").matches(expense(amount=100.0)))
        self.assertFalse(parse_filter("amount>100").matches(expense(amount=100.0)))
        self.assertTrue(parse_filter("amount<100").matches(expense(amount=99.99)))
        self.assertTrue(parse_filter("amount<=100").matches(expense(amount=100.0)))
        self.assertTrue(parse_filter("amount==100").matches(expense(amount=100.0)))
        self.assertTrue(parse_filter("amount!=100").matches(expense(amount=99.0)))

    def test_single_equals_is_equality(self):
        self.assertTrue(parse_filter("amount=100").matches(expense(amount=100.0)))

    def test_spaces_around_parts(self):
        self.assertTrue(parse_filter(" amount >= 100 ").matches(expense(amount=100.0)))

    def test_category_equality(self):
        self.assertTrue(parse_filter("category=餐饮").matches(expense(category="餐饮")))
        self.assertFalse(parse_filter("category=餐饮").matches(expense(category="交通")))
        self.assertTrue(parse_filter("category!=餐饮").matches(expense(category="交通")))

    def test_category_can_contain_spaces(self):
        self.assertTrue(parse_filter("category=餐饮 娱乐").matches(expense(category="餐饮 娱乐")))

    def test_date_comparison(self):
        self.assertTrue(parse_filter("date>=2026-02-01").matches(expense("2026-02-01")))
        self.assertFalse(parse_filter("date>2026-02-01").matches(expense("2026-02-01")))
        self.assertTrue(parse_filter("date=2026-02-01").matches(expense("2026-02-01")))


class ParseFilterErrorTest(unittest.TestCase):
    def assert_col(self, expression: str, expected_col: int):
        try:
            parse_filter(expression)
        except FilterError as exc:
            self.assertEqual(expected_col, caret_column(str(exc)), msg=str(exc))
        else:
            self.fail(f"应当报错：{expression}")

    def test_empty_expression(self):
        self.assert_col("   ", 0)

    def test_unknown_column_points_at_column(self):
        self.assert_col("amt>=100", 0)

    def test_unknown_operator_points_at_operator(self):
        self.assert_col("amount=>100", 6)

    def test_no_operator_points_at_missing_operator(self):
        self.assert_col("amount100", len("amount"))

    def test_missing_value_points_at_end(self):
        self.assert_col("amount>=", len("amount>="))

    def test_bad_number_points_at_value(self):
        self.assert_col("amount>=abc", len("amount>="))

    def test_bad_date_points_at_value(self):
        self.assert_col("date=2026/02/01", len("date="))

    def test_category_ordering_not_allowed(self):
        self.assert_col("category>餐饮", len("category"))

    def test_error_message_keeps_expression(self):
        try:
            parse_filter("amount>=abc")
        except FilterError as exc:
            message = str(exc)
        else:
            self.fail("应当报错")
        self.assertIn("amount>=abc", message)
        self.assertIn("^", message)


class ApplyFilterTest(unittest.TestCase):
    def test_keeps_matching_rows_in_order(self):
        rows = [
            expense("2026-02-01", amount=10.0),
            expense("2026-02-02", amount=200.0),
            expense("2026-02-03", amount=300.0),
        ]
        kept = apply_filter(rows, parse_filter("amount>=200"))
        self.assertEqual([200.0, 300.0], [row.amount for row in kept])

    def test_none_filter_returns_all(self):
        rows = [expense(amount=10.0), expense(amount=20.0)]
        self.assertEqual(rows, apply_filter(rows, None))


if __name__ == "__main__":
    unittest.main()
