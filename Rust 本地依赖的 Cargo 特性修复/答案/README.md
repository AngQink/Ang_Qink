# Rust 本地依赖的 Cargo 特性修复 / Rust Cargo Feature Resolution with Local Dependencies

## 解析

Cargo 会在同一个依赖图合并特性。根依赖关闭默认特性，两个公开配置各自只向下游开启同一种方言。仅验证 baseline 无法发现 next 回退到旧配置。

[参考解](reference/Cargo.toml) 和[正式评测](评测/grade.py)可分别查看。60 组任务由冻结种子生成，并检查最终产物。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Cargo unifies enabled features throughout a dependency graph. Disable dependency defaults at the root and forward only the chosen dialect. A passing baseline build cannot detect next silently selecting legacy.

See the [reference](reference/Cargo.toml) and [evaluator](评测/grade.py). The evaluator uses 60 frozen seeds and inspects the resulting artifacts.
