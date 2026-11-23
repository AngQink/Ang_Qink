# Python 检查点与残缺事务日志恢复 / Python Recovery from Checkpoints and Torn Journals

## 解析

每笔开始时复制已提交键值，处理写入但只在确认时推进版本。有效 JSON 即使字节完整，缺失换行符也不能当作持久化的确认记录。

[参考解](reference/recover.py) 和[正式评测](评测/grade.py)可分别查看。60 组任务由冻结种子生成，并检查最终产物。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Copy committed values when staging a transaction. Advance the revision only at commit. Even valid JSON without the final newline is not a durable commit.

See the [reference](reference/recover.py) and [evaluator](评测/grade.py). The evaluator uses 60 frozen seeds and inspects the resulting artifacts.
