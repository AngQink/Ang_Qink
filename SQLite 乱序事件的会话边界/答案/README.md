# SQLite 乱序事件的会话边界 / Session Boundaries for Out-of-Order Events

## 解析

用 LAG 找按时序的前一条事件，用窗口累加得到分段编号。先计算全段聚合，再按原始行序回写。

[参考实现](reference/main.sql) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Use LAG in event-time order to find gaps. A cumulative sum labels segments. Compute whole-segment aggregates and restore input order.

The [reference implementation](reference/main.sql) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.
