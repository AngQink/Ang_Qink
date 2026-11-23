# VBScript 旧归档任务重放的缺陷修复 / VBScript Legacy archival-job replay Repair

## 解析

先验证代号等于当前代，再检查序号政策与新余额。提交前不得改动任何字段。旧代可以携带看起来合法的新序号，这是故障复现的关键。

[参考实现](reference/main.vbs) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Match the epoch first, then check the sequence policy and next balance. Do not mutate before all checks pass. An obsolete epoch can carry an otherwise valid sequence, which reproduces the bug.

The [reference implementation](reference/main.vbs) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.
