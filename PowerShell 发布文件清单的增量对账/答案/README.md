# PowerShell 发布文件清单的增量对账 / PowerShell Release Artifact Inventory Diff

## 解析

先生成规范路径到摘要的字典，再按有序并集区分新增、替换与删除。摘要比较使用内容，文件时间不参与判断。

[参考解](reference/main.ps1) 和[正式评测](评测/grade.py)可分别查看。60 组任务由冻结种子生成，并检查最终产物。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Build a map from normalized paths to content hashes, then iterate the sorted union to distinguish additions, replacements, and removals. File times play no part.

See the [reference](reference/main.ps1) and [evaluator](评测/grade.py). The evaluator uses 60 frozen seeds and inspects the resulting artifacts.
