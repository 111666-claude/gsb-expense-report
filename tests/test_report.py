import unittest
from datetime import date

from expense_report.csvio import Expense
from expense_report.report import (
    format_amount,
    format_month_report,
    format_percent,
    format_report,
    format_top_report,
    format_week_report,
    group_by_day,
    group_by_month,
    group_by_week,
    top_categories,
)


def make(day: int, amount: float, category: str = "餐饮") -> Expense:
    return Expense(day=date(2026, 2, day), category=category, amount=amount)


def expense(text: str, amount: float, category: str = "餐饮") -> Expense:
    return Expense(day=date.fromisoformat(text), category=category, amount=amount)


class GroupByDayTest(unittest.TestCase):
    def test_sums_same_day(self):
        rows = group_by_day([make(1, 10.0), make(1, 5.0), make(2, 7.0)])
        self.assertEqual([(date(2026, 2, 1), 15.0), (date(2026, 2, 2), 7.0)], rows)

    def test_sorted_by_day(self):
        rows = group_by_day([make(3, 1.0), make(1, 1.0), make(2, 1.0)])
        self.assertEqual([1, 2, 3], [row[0].day for row in rows])


class GroupByWeekTest(unittest.TestCase):
    def test_iso_week_monday_start(self):
        rows = group_by_week(
            [
                expense("2026-02-01", 10.0),  # 周日，W05
                expense("2026-02-02", 20.0),  # 周一，W06
            ]
        )
        self.assertEqual([("2026-W05", 10.0), ("2026-W06", 20.0)], rows)

    def test_week_spans_month_boundary(self):
        rows = group_by_week(
            [
                expense("2026-01-31", 100.0),  # 周六
                expense("2026-02-01", 50.0),   # 周日，同一 ISO 周
            ]
        )
        self.assertEqual([("2026-W05", 150.0)], rows)

    def test_week_spans_year_boundary(self):
        rows = group_by_week(
            [
                expense("2022-12-31", 10.0),  # 周六，ISO 2022-W52
                expense("2023-01-01", 20.0),  # 周日，仍属 ISO 2022-W52
                expense("2023-01-02", 40.0),  # 周一，ISO 2023-W01
                expense("2025-12-29", 5.0),   # 周一，ISO 2026-W01
            ]
        )
        self.assertEqual(
            [
                ("2022-W52", 30.0),
                ("2023-W01", 40.0),
                ("2026-W01", 5.0),
            ],
            rows,
        )

    def test_week_report_renders_labels(self):
        text = format_week_report([("2026-W05", 225.5)])
        self.assertIn("2026-W05", text)
        self.assertIn("W05", text)
        self.assertIn("225.50", text)


class GroupByMonthTest(unittest.TestCase):
    def test_spans_months_and_years(self):
        rows = group_by_month(
            [
                expense("2026-01-31", 10.0),
                expense("2026-02-01", 20.0),
                expense("2026-03-01", 30.0),
                expense("2025-12-31", 40.0),
            ]
        )
        self.assertEqual(
            [
                ("2025-12", 40.0),
                ("2026-01", 10.0),
                ("2026-02", 20.0),
                ("2026-03", 30.0),
            ],
            rows,
        )

    def test_month_report_renders(self):
        text = format_month_report([("2026-02", 840.5)])
        self.assertIn("2026-02", text)
        self.assertIn("840.50", text)


class TopCategoriesTest(unittest.TestCase):
    def test_amount_desc_then_category_name(self):
        rows = top_categories(
            [
                expense("2026-02-01", 10.0, "购物"),
                expense("2026-02-01", 10.0, "餐饮"),
                expense("2026-02-01", 10.0, "交通"),
                expense("2026-02-01", 30.0, "住房"),
            ],
            2,
        )
        self.assertEqual([("住房", 30.0), ("交通", 10.0)], rows)

    def test_tie_order_stable_independent_of_insertion(self):
        data = [
            expense("2026-02-01", 10.0, name)
            for name in ("交通", "餐饮", "购物")
        ]
        first = top_categories(data, 3)
        second = top_categories(list(reversed(data)), 3)
        self.assertEqual(first, second)
        self.assertEqual(["交通", "购物", "餐饮"], [name for name, _ in first])

    def test_limit_cuts_rows(self):
        rows = top_categories([make(1, 1.0, "甲"), make(1, 2.0, "乙")], 1)
        self.assertEqual([("乙", 2.0)], rows)

    def test_report_shares_one_decimal(self):
        text = format_top_report([("餐饮", 550.5), ("购物", 460.0)], 1096.0)
        self.assertIn("50.2%", text)
        self.assertIn("42.0%", text)
        self.assertIn("1010.50", text)

    def test_percent_zero_total(self):
        self.assertEqual("0.0%", format_percent(0.0, 0.0))


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
