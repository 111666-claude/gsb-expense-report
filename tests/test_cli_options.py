import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from expense_report.cli import main

CSV = (
    "date,category,amount\n"
    "2025-12-29,餐饮,10.00\n"
    "2026-01-04,餐饮,20.00\n"
    "2026-02-01,购物,340.00\n"
    "2026-03-01,交通,45.00\n"
)


class CliOptionTest(unittest.TestCase):
    def run_cli(self, folder: str, *args: str) -> tuple[int, str]:
        path = os.path.join(folder, "data.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(CSV)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["--file", path, *args])
        return code, buffer.getvalue()

    def test_week_group_spans_year_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            code, output = self.run_cli(folder, "--group-by", "week")
        self.assertEqual(0, code)
        self.assertIn("W01", output)
        self.assertIn("30.00", output)
        self.assertNotIn("2025-12-29", output)
        self.assertNotIn("2026-01-04", output)

    def test_month_group(self):
        with tempfile.TemporaryDirectory() as folder:
            code, output = self.run_cli(folder, "--group-by", "month")
        self.assertEqual(0, code)
        self.assertIn("2025-12     10.00", output)
        self.assertIn("2026-02    340.00", output)
        self.assertIn("2026-03     45.00", output)

    def test_top_outputs_categories_and_percent(self):
        with tempfile.TemporaryDirectory() as folder:
            code, output = self.run_cli(folder, "--top", "2")
        self.assertEqual(0, code)
        self.assertIn("购物", output)
        self.assertIn("340.00", output)
        self.assertIn("81.9%", output)
        self.assertIn("交通", output)
        self.assertNotIn("餐饮", output)

    def test_filter_applied_before_grouping(self):
        with tempfile.TemporaryDirectory() as folder:
            code, output = self.run_cli(folder, "--filter", "amount>=100")
        self.assertEqual(0, code)
        self.assertIn("340.00", output)
        self.assertNotIn("45.00", output)
        self.assertNotIn("30.00", output)

    def test_filter_category(self):
        with tempfile.TemporaryDirectory() as folder:
            code, output = self.run_cli(folder, "--filter", "category=餐饮")
        self.assertEqual(0, code)
        self.assertIn("30.00", output)
        self.assertNotIn("340.00", output)

    def test_bad_filter_returns_two_with_position(self):
        with tempfile.TemporaryDirectory() as folder:
            code, output = self.run_cli(folder, "--filter", "amount>>1")
        self.assertEqual(2, code)
        self.assertIn("过滤表达式有误", output)
        self.assertIn("^", output)

    def test_top_with_week_group_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            code, output = self.run_cli(folder, "--top", "1", "--group-by", "week")
        self.assertEqual(2, code)
        self.assertIn("参数冲突", output)

    def test_top_with_month_group_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            code, output = self.run_cli(folder, "--top", "1", "--group-by", "month")
        self.assertEqual(2, code)

    def test_invalid_group_choice_exits_two(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(SystemExit) as context:
                self.run_cli(folder, "--group-by", "year")
        self.assertEqual(2, context.exception.code)

    def test_invalid_top_exits_two(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(SystemExit) as context:
                self.run_cli(folder, "--top", "0")
        self.assertEqual(2, context.exception.code)


if __name__ == "__main__":
    unittest.main()
