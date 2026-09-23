# expense-report

把消费流水 CSV 汇总成按天报表的小工具，只用 Python 标准库。

```
python3 -m expense_report.cli --file sample/expenses.csv
python3 -m unittest discover -s tests -v
```

## 输入格式

CSV 表头必须是 `date,category,amount`（可以多出别的列）：

```
date,category,amount
2026-02-01,餐饮,80.00
2026-02-01,交通,25.00
```

- `date`：`YYYY-MM-DD`
- `category`：非空字符串
- `amount`：非负数字

行不合法时不会中断整个文件，会直接报错并指出行号。

## 输出

```
日期        金额
--------------------
2026-01-31    120.50
2026-02-01    105.00
--------------------
合计          225.50
```

## 目录

```
expense_report/
  csvio.py    读取与校验 CSV
  report.py   汇总与表格输出
  cli.py      命令行入口
tests/        unittest 用例
sample/expenses.csv  示例流水
```
