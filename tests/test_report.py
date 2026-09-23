import unittest
from datetime import date

from expense_report.csvio import Expense
from expense_report.report import format_amount, format_report, group_by_day


def make(day: int, amount: float, category: str = "餐饮") -> Expense:
    return Expense(day=date(2026, 2, day), category=category, amount=amount)


class GroupByDayTest(unittest.TestCase):
    def test_sums_same_day(self):
        rows = group_by_day([make(1, 10.0), make(1, 5.0), make(2, 7.0)])
        self.assertEqual([(date(2026, 2, 1), 15.0), (date(2026, 2, 2), 7.0)], rows)

    def test_sorted_by_day(self):
        rows = group_by_day([make(3, 1.0), make(1, 1.0), make(2, 1.0)])
        self.assertEqual([1, 2, 3], [row[0].day for row in rows])


class FormatTest(unittest.TestCase):
    def test_amount_keeps_two_decimals(self):
        self.assertEqual("15.50", format_amount(15.5))

    def test_report_contains_total(self):
        text = format_report([(date(2026, 2, 1), 15.5)])
        self.assertIn("2026-02-01", text)
        self.assertIn("合计", text)
        self.assertIn("15.50", text)


if __name__ == "__main__":
    unittest.main()
