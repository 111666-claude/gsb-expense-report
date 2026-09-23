import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from expense_report.cli import main


class MainTest(unittest.TestCase):
    def write(self, folder: str, text: str) -> str:
        path = os.path.join(folder, "data.csv")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_prints_day_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n2026-02-01,餐饮,80\n")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["--file", path])
        self.assertEqual(0, code)
        self.assertIn("2026-02-01", buffer.getvalue())
        self.assertIn("80.00", buffer.getvalue())

    def test_bad_file_returns_two(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, "date,category,amount\n2026-02-01,餐饮,abc\n")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["--file", path])
        self.assertEqual(2, code)
        self.assertIn("读取失败", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
