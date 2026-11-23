# Rust 序列化配置的版本迁移 / Rust Serialized configuration Version Migration

## 解析

分别管理旧值的存在性、归一化数值与覆盖策略。只在导入时做舍入和来源转换，显式零不能变成缺失。

[参考实现](reference/main.rs) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Track legacy presence, normalized value, and override policy separately. Round and apply the origin offset only on import. Explicit zero remains present.

The [reference implementation](reference/main.rs) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.
