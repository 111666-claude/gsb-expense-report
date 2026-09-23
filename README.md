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
  - `day`：按天汇总（默认行为，输出格式不变）。
  - `week`：按 ISO 周汇总，周一起算；标签形如 `2026-W05`，跨年时以 ISO 周年为准。
  - `month`：按月汇总；标签形如 `2026-02`。
- `--top N`：不输出时间维度报表，改为按类别汇总金额，输出金额最高的 N 个类别及各自占比（保留一位小数）。金额相同时按类别名升序排列。不能与 `--group-by week/month` 同时使用。
- `--filter '列 比较符 数值'`：只统计满足条件的记录，可与上面两个参数任意组合。
  - 列：`date`、`category`、`amount`。
  - 比较符：`>=`、`<=`、`==`、`!=`、`>`、`<`、`=`（`==` 与 `=` 等价；`category` 只支持相等类比较）。
  - 值：`amount` 为数字，`date` 为 `YYYY-MM-DD`，`category` 为字符串。
  - 等号两侧的空格可有可无，例如 `amount>=100` 与 `amount >= 100` 等价。
  - 表达式写错时报错并指出出错位置（第几个字符），退出码为 2。

## 输出

默认按天：

```
日期        金额
--------------------
2026-01-31    120.50
2026-02-01    105.00
--------------------
合计         1096.00
```

按 ISO 周（`--group-by week`）：

```
周        金额
--------------------
2026-W05    225.50
2026-W06    555.50
2026-W07    180.00
2026-W09     45.00
2026-W10     90.00
--------------------
合计       1096.00
```

按月（`--group-by month`）：

```
月份      金额
--------------------
2026-01     120.50
2026-02     840.50
2026-03     135.00
--------------------
合计       1096.00
```

类别 Top N（`--top 2`）：

```
类别      金额        占比
--------------------------
餐饮        550.50   50.2%
购物        460.00   42.0%
--------------------------
合计       1010.50   92.2%
```

占比分母是全部（过滤后的）流水总额；合计行是展示出来的 N 个类别之和。

## 示例

```
python3 -m expense_report.cli --file sample/expenses.csv --group-by week
python3 -m expense_report.cli --file sample/expenses.csv --group-by month
python3 -m expense_report.cli --file sample/expenses.csv --top 2
python3 -m expense_report.cli --file sample/expenses.csv --filter 'amount>=100'
python3 -m expense_report.cli --file sample/expenses.csv --filter 'category=餐饮' --group-by week
python3 -m expense_report.cli --file sample/expenses.csv --filter 'date >= 2026-02-01' --top 3
```

错误示例（会标出出错位置）：

```
$ python3 -m expense_report.cli --file sample/expenses.csv --filter 'amount>>100'
过滤条件有误（第 8 个字符）：比较符应为 >=、<=、==、!=、>、<、=
  amount>>100
         ^
```

## 目录

```
expense_report/
  csvio.py    读取与校验 CSV
  report.py   汇总（天/周/月、类别 Top）与表格输出
  filter.py   过滤表达式解析、校验与应用
  cli.py      命令行入口
tests/        unittest 用例
sample/expenses.csv  示例流水
```
