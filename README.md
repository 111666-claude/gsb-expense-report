# expense-report

把消费流水 CSV 汇总成报表的小工具，只用 Python 标准库。

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

## 参数

- `--file PATH`：消费流水 CSV 路径（必填）。
- `--group-by day|week|month`：汇总粒度，默认 `day`。
  - `day`：按天（默认行为，输出与不传该参数时逐字节一致）。
  - `week`：按 ISO 周汇总，周一为每周第一天，标签如 `W05`；跨年的周按
    ISO 周年归并（例如 2025-12-29 到 2026-01-04 同属 `W01`），非 2026
    ISO 年的周带年份前缀，如 `2025-W01`。
  - `month`：按月汇总，标签为 `YYYY-MM`，跨年边界自然分开。
- `--top N`：改为按类别汇总，输出金额最高的 N 个类别及各自占总计的百分比
  （保留一位小数）。金额相同时按类别名升序，输出稳定。不能与
  `--group-by week|month` 同时使用。
- `--filter '列 比较符 数值'`：只统计满足条件的记录。
  - 列：`amount`、`category`、`date`；比较符两侧可以有空格。
  - `amount`、`date` 支持 `>= <= > < = == !=`；`category` 是文本列，只支持
    `=`、`==`、`!=`。
  - 例如 `amount>=100`、`category=餐饮`、`date>=2026-02-01`。
  - 表达式写错时退出码为 2，错误信息用 `^` 指出出错位置。

非法参数（未知的 `--group-by` 取值、`--top` 非正整数、`--top` 与
`--group-by week|month` 组合等）退出码均为 2。

## 输出

按天（默认）：

```
日期        金额
--------------------
2026-01-31    120.50
2026-02-01    105.00
--------------------
合计          225.50
```

按 ISO 周（`--group-by week`，示例数据）：

```
周        金额
--------------------
W05    225.50
W06    555.50
W07    180.00
W09     45.00
W10     90.00
--------------------
合计         1096.00
```

按月（`--group-by month`，示例数据）：

```
月份        金额
--------------------
2026-01    120.50
2026-02    840.50
2026-03    135.00
--------------------
合计         1096.00
```

类别 Top N（`--top 2`，示例数据，总计 1096.00）：

```
类别          金额    占比
--------------------------
餐饮        550.50   50.2%
购物        460.00   42.0%
--------------------------
合计       1096.00  100.0%
```

参数可以组合，例如只看百元以上的大额消费再按周汇总：

```
python3 -m expense_report.cli --file sample/expenses.csv --group-by week --filter 'amount>=100'
```

## 目录

```
expense_report/
  csvio.py      读取与校验 CSV
  report.py     按天/周/月与类别汇总、表格输出
  filtering.py  --filter 表达式解析与执行
  cli.py        命令行入口
tests/          unittest 用例
sample/expenses.csv  示例流水
```
