# C++ 双配置 CMake 构建修复 / C++ Dual-Profile CMake Build Repair

## 解析

生成配置应来自构建目录，并只对依赖该配置的目标设置包含目录。将每个配置构建到不同目录，避免读错上一次生成的头。

[参考解](reference/CMakeLists.txt) 和[正式评测](评测/grade.py)可分别查看。60 组任务由冻结种子生成，并检查最终产物。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Generate the configuration in the build tree and give the consuming library the matching include path. Separate build directories prevent an old generated header from being reused.

See the [reference](reference/CMakeLists.txt) and [evaluator](评测/grade.py). The evaluator uses 60 frozen seeds and inspects the resulting artifacts.
