import os
import tempfile
import unittest

from expense_report.csvio import CsvError, parse_date, parse_row, read_expenses, total_of


class ParseDateTest(unittest.TestCase):
    def test_ok(self):
        self.assertEqual((2026, 2, 1), (parse_date("2026-02-01").year, parse_date("2026-02-01").month, parse_date("2026-02-01").day))

    def test_bad(self):
        with self.assertRaises(CsvError):
            parse_date("2026/02/01")


class ParseRowTest(unittest.TestCase):
    def test_ok(self):
        expense = parse_row({"date": "2026-02-01", "category": " 餐饮 ", "amount": "80.00"}, 2)
        self.assertEqual("餐饮", expense.category)
        self.assertEqual(80.0, expense.amount)

    def test_empty_category(self):
        with self.assertRaises(CsvError):
            parse_row({"date": "2026-02-01", "category": "  ", "amount": "1"}, 2)

    def test_negative_amount(self):
        with self.assertRaises(CsvError):
            parse_row({"date": "2026-02-01", "category": "餐饮", "amount": "-1"}, 2)

    def test_not_a_number(self):
        with self.assertRaises(CsvError):
            parse_row({"date": "2026-02-01", "category": "餐饮", "amount": "abc"}, 3)


class ReadExpensesTest(unittest.TestCase):
    def write(self, folder: str, text: str) -> str:
        path = os.path.join(folder, "data.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_reads_and_totals(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n2026-02-01,餐饮,80\n2026-02-02,交通,20\n")
            expenses = read_expenses(path)
        self.assertEqual(2, len(expenses))
        self.assertEqual(100.0, total_of(expenses))

    def test_missing_column(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category\n2026-02-01,餐饮\n")
            with self.assertRaises(CsvError):
                read_expenses(path)


if __name__ == "__main__":
    unittest.main()
