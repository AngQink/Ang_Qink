# SQLite 重叠有效期的优先级归并 / Priority Resolution for Overlapping Effective Intervals

## 解析

将可见性与区间过滤放在候选排序之前。最高优先级比较后，再按长度和稳定行序决出同分记录。

[参考实现](reference/main.sql) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Filter by visibility and interval first, then rank candidates by priority, width, and stable arrival order.

The [reference implementation](reference/main.sql) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.
