import unittest
from datetime import date

from expense_report.csvio import Expense
from expense_report.report import group_by_day, group_by_month, group_by_week


def expense(year: int, month: int, day: int, amount: float, category: str = "餐饮") -> Expense:
    return Expense(day=date(year, month, day), category=category, amount=amount)


class GroupByWeekTest(unittest.TestCase):
    def test_week_starts_on_monday(self):
        rows = group_by_week([expense(2026, 2, 1, 10.0), expense(2026, 2, 2, 20.0)])
        self.assertEqual([("W05", 10.0), ("W06", 20.0)], rows)

    def test_saturday_and_sunday_share_one_week(self):
        rows = group_by_week([expense(2026, 1, 31, 100.0), expense(2026, 2, 1, 25.50)])
        self.assertEqual([("W05", 125.50)], rows)

    def test_iso_week_spans_month_boundary(self):
        rows = group_by_week([
            expense(2026, 1, 26, 1.0),
            expense(2026, 2, 1, 2.0),
        ])
        self.assertEqual([("W05", 3.0)], rows)

    def test_iso_week_spans_year_boundary(self):
        # 2025-12-29（周一）到 2026-01-04（周日）都属于 ISO 2026 年第 1 周
        rows = group_by_week([
            expense(2025, 12, 29, 1.0),
            expense(2025, 12, 31, 2.0),
            expense(2026, 1, 1, 3.0),
            expense(2026, 1, 4, 4.0),
        ])
        self.assertEqual([("W01", 10.0)], rows)

    def test_weeks_from_different_years_stay_distinct_and_sorted(self):
        # 2024-12-30（周一）属于 ISO 2025-W01；2025-12-29 属于 ISO 2026-W01
        rows = group_by_week([
            expense(2025, 12, 29, 20.0),
            expense(2024, 12, 30, 10.0),
        ])
        self.assertEqual([("2025-W01", 10.0), ("W01", 20.0)], rows)

    def test_weeks_sorted_chronologically(self):
        rows = group_by_week([
            expense(2026, 3, 2, 4.0),
            expense(2026, 1, 5, 1.0),
            expense(2026, 2, 9, 3.0),
        ])
        self.assertEqual(["W02", "W07", "W10"], [label for label, _ in rows])


class GroupByMonthTest(unittest.TestCase):
    def test_sums_within_month(self):
        rows = group_by_month([
            expense(2026, 2, 1, 80.0),
            expense(2026, 2, 28, 20.0),
            expense(2026, 3, 1, 5.0),
        ])
        self.assertEqual([("2026-02", 100.0), ("2026-03", 5.0)], rows)

    def test_cross_year_boundary_and_sorting(self):
        rows = group_by_month([
            expense(2026, 12, 31, 3.0),
            expense(2025, 12, 31, 1.0),
            expense(2026, 1, 1, 2.0),
        ])
        self.assertEqual(
            [("2025-12", 1.0), ("2026-01", 2.0), ("2026-12", 3.0)],
            rows,
        )


class GroupByDayStillWorksTest(unittest.TestCase):
    def test_unchanged(self):
        rows = group_by_day([expense(2026, 2, 1, 1.0), expense(2026, 1, 31, 2.0)])
        self.assertEqual([(date(2026, 1, 31), 2.0), (date(2026, 2, 1), 1.0)], rows)


if __name__ == "__main__":
    unittest.main()
