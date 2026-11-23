# SQLite 修订流的历史读取 / As-of Reads over a Revision Stream

## 解析

将重置行累计成会话分区，在同一会话中仅枚举之前的候选写入。业务版本与物理行号都要排序，删除标记也参与排序。

[参考实现](reference/main.sql) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Partition by cumulative resets. Rank only earlier eligible writes by both business revision and physical row order. Tombstones participate in that ranking.

The [reference implementation](reference/main.sql) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.
