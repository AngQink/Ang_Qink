# Fortran 求解器检查点的故障恢复 / Fortran Solver checkpoints Crash Recovery

## 解析

把已提交与待提交拆开。校验失败保留可重试记录，崩溃则丢掉该记录。后续旧确认不能绕过待提交版本检查。

[参考实现](reference/main.f90) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Separate committed and pending records. A bad checksum preserves the pending entry for retry. A crash discards that entry, so a late acknowledgment cannot commit it.

The [reference implementation](reference/main.f90) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.
