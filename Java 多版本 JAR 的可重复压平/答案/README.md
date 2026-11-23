# Java 多版本 JAR 的可重复压平 / Java Reproducible Flattening of Multi-Release JARs

## 解析

在解压时按逻辑路径选最高可用版本。写入时先设置大小、CRC32 和 DOS 时间，再按固定顺序提交 STORED 成员。实际启动 JAR 再检查资源查找。

[参考解](reference/Main.java) 和[正式评测](评测/grade.py)可分别查看。60 组任务由冻结种子生成，并检查最终产物。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Select by logical path and compatible release before writing. Set CRC32, sizes, and DOS timestamps, then emit entries in canonical order. Launching the result also checks resource lookup.

See the [reference](reference/Main.java) and [evaluator](评测/grade.py). The evaluator uses 60 frozen seeds and inspects the resulting artifacts.
