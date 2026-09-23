import unittest
from datetime import date

from expense_report.csvio import Expense
from expense_report.report import format_top, top_categories


def expense(category: str, amount: float) -> Expense:
    return Expense(day=date(2026, 2, 1), category=category, amount=amount)


class TopCategoriesTest(unittest.TestCase):
    def test_sums_and_orders_by_amount_desc(self):
        rows = top_categories(
            [expense("餐饮", 100.0), expense("购物", 200.0), expense("交通", 50.0)],
            3,
        )
        self.assertEqual(["购物", "餐饮", "交通"], [category for category, _, _ in rows])
        self.assertEqual([200.0, 100.0, 50.0], [amount for _, amount, _ in rows])

    def test_tie_breaks_by_category_name_ascending(self):
        rows = top_categories(
            [expense("b", 10.0), expense("a", 10.0), expense("c", 5.0)],
            3,
        )
        self.assertEqual([("a", 10.0), ("b", 10.0), ("c", 5.0)],
                         [(category, amount) for category, amount, _ in rows])

    def test_tie_break_is_stable_for_unicode_names(self):
        rows = top_categories(
            [expense("餐饮", 10.0), expense("购物", 10.0)],
            2,
        )
        self.assertEqual(sorted(["餐饮", "购物"]), [category for category, _, _ in rows])

    def test_limit_truncates(self):
        rows = top_categories(
            [expense("a", 3.0), expense("b", 2.0), expense("c", 1.0)],
            2,
        )
        self.assertEqual(["a", "b"], [category for category, _, _ in rows])

    def test_percentages_keep_one_decimal(self):
        rows = top_categories(
            [expense("餐饮", 550.50), expense("购物", 460.00),
             expense("交通", 85.50)],
            3,
        )
        self.assertEqual((550.50, 50.2), (rows[0][1], round(rows[0][2], 1)))
        self.assertEqual((460.00, 42.0), (rows[1][1], round(rows[1][2], 1)))

    def test_empty_input(self):
        self.assertEqual([], top_categories([], 3))


class FormatTopTest(unittest.TestCase):
    def test_contains_category_amount_percent_and_total(self):
        text = format_top([("餐饮", 550.50, 50.2), ("购物", 460.00, 42.0)], 1096.00)
        self.assertIn("餐饮", text)
        self.assertIn("550.50", text)
        self.assertIn("50.2%", text)
        self.assertIn("1096.00", text)
        self.assertIn("合计", text)


if __name__ == "__main__":
    unittest.main()
