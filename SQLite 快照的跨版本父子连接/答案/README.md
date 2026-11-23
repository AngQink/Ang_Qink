# SQLite 快照的跨版本父子连接 / Revision-aware Joins for SQLite Snapshots

## 解析

对子记录和父记录分别排名，父记录的上界取已选子版本。查询快照由当前行界定，允许晚于子记录发布父修订。

[参考实现](reference/main.sql) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Rank children and parents separately. The selected child's revision is the parent ceiling. Visibility still ends at the query row, so parent corrections arriving after the child can apply.

The [reference implementation](reference/main.sql) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.
