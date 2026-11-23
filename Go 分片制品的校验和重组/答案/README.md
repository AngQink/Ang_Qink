# Go 分片制品的校验和重组 / Go Checksummed Artifact Reconstruction

## 解析

验证每个候选后才更新该位置。用独立的存在性标志区分空数据和缺失。所有位置确认后再生成完整二进制产物。

[参考解](reference/main.go) 和[正式评测](评测/grade.py)可分别查看。60 组任务由冻结种子生成，并检查最终产物。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Validate a candidate before updating its slot. Track presence separately from the bytes so an empty fragment is still valid. Check all positions before emitting the artifact.

See the [reference](reference/main.go) and [evaluator](评测/grade.py). The evaluator uses 60 frozen seeds and inspects the resulting artifacts.
