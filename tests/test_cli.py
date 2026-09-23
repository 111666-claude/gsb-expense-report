import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from expense_report.cli import main

SAMPLE_ROWS = (
    "2026-01-31,餐饮,120.50\n"
    "2026-02-01,餐饮,80.00\n"
    "2026-02-01,交通,25.00\n"
    "2026-02-02,餐饮,200.00\n"
    "2026-02-02,交通,15.50\n"
    "2026-02-03,购物,340.00\n"
    "2026-02-09,餐饮,60.00\n"
    "2026-02-09,购物,120.00\n"
    "2026-03-01,交通,45.00\n"
    "2026-03-02,餐饮,90.00\n"
)


class MainTest(unittest.TestCase):
    def write(self, folder: str, text: str) -> str:
        path = os.path.join(folder, "data.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def invoke(self, path: str, *extra: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["--file", path, *extra])
        return code, buffer.getvalue()

    def test_prints_day_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n2026-02-01,餐饮,80\n")
            code, output = self.invoke(path)
        self.assertEqual(0, code)
        self.assertIn("2026-02-01", output)
        self.assertIn("80.00", output)

    def test_default_output_is_byte_stable(self):
        expected = (
            "日期        金额\n"
            "--------------------\n"
            "2026-02-01     80.00\n"
            "--------------------\n"
            "合计           80.00\n"
        )
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n2026-02-01,餐饮,80\n")
            code, output = self.invoke(path)
        self.assertEqual(0, code)
        self.assertEqual(expected, output)

    def test_bad_file_returns_two(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n2026-02-01,餐饮,abc\n")
            code, output = self.invoke(path)
        self.assertEqual(2, code)
        self.assertIn("读取失败", output)

    def test_week_grouping_on_sample(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n" + SAMPLE_ROWS)
            code, output = self.invoke(path, "--group-by", "week")
        self.assertEqual(0, code)
        for fragment in (
            "2026-W05    225.50",
            "2026-W06    555.50",
            "2026-W07    180.00",
            "2026-W09     45.00",
            "2026-W10     90.00",
            "合计       1096.00",
        ):
            self.assertIn(fragment, output)

    def test_month_grouping_on_sample(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n" + SAMPLE_ROWS)
            code, output = self.invoke(path, "--group-by", "month")
        self.assertEqual(0, code)
        self.assertIn("2026-01     120.50", output)
        self.assertIn("2026-02     840.50", output)
        self.assertIn("2026-03     135.00", output)

    def test_top_two_on_sample(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n" + SAMPLE_ROWS)
            code, output = self.invoke(path, "--top", "2")
        self.assertEqual(0, code)
        self.assertIn("餐饮        550.50   50.2%", output)
        self.assertIn("购物        460.00   42.0%", output)

    def test_tied_categories_sorted_by_name(self):
        data = (
            "2026-02-01,交通,10\n"
            "2026-02-01,餐饮,10\n"
            "2026-02-01,购物,10\n"
        )
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n" + data)
            code, output = self.invoke(path, "--top", "3")
        self.assertEqual(0, code)
        self.assertLess(output.index("交通"), output.index("购物"))
        self.assertLess(output.index("购物"), output.index("餐饮"))

    def test_filter_amount(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n" + SAMPLE_ROWS)
            code, output = self.invoke(path, "--filter", "amount>=100")
        self.assertEqual(0, code)
        self.assertIn("780.50", output)
        self.assertNotIn("45.00", output)

    def test_filter_error_points_at_position(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n" + SAMPLE_ROWS)
            code, output = self.invoke(path, "--filter", "amount>>100")
        self.assertEqual(2, code)
        self.assertIn("过滤条件有误", output)
        self.assertIn("第 8 个字符", output)
        self.assertIn("^", output)

    def test_top_conflicts_with_group_by_week(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n" + SAMPLE_ROWS)
            code, output = self.invoke(path, "--group-by", "week", "--top", "2")
        self.assertEqual(2, code)
        self.assertIn("参数错误", output)

    def test_invalid_group_by(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n" + SAMPLE_ROWS)
            code, output = self.invoke(path, "--group-by", "year")
        self.assertEqual(2, code)
        self.assertIn("--group-by", output)

    def test_invalid_top(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n" + SAMPLE_ROWS)
            code, output = self.invoke(path, "--top", "0")
        self.assertEqual(2, code)
        self.assertIn("--top", output)


if __name__ == "__main__":
    unittest.main()
