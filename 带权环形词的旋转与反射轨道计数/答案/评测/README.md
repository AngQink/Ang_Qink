# 正式评测 / Official Evaluation

## 中文

原正式套件共 96 场，其中 16 场当时公开、80 场当时隐藏。`题目/public_tests` 的快速自测与其中的公开场景存在重合。

在当前这道题的目录运行以下命令。第一条使用随附参考实现。第二条评测你在 `题目` 中完成的实现，并在新建的 `report` 目录保存逐项结果。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目 --output report
```

裁判使用 Windows 的进程内存统计，建议使用题面中的 CPython 版本。报告记录实际通过数、错误及原裁判支持的耗时和内存指标。直接运行时，报告存放在自动清理的临时目录。输入与预期结果由 `judge` 中的原用例文件或模型生成。

## English

The original suite has 96 scenarios. 16 were public and 80 were hidden during the match. The quick tests in `题目/public_tests` overlap with the public scenarios in this suite.

Run these commands from this problem's directory. The first uses the bundled reference. The second evaluates your implementation in `题目` and writes the per-case report to a new `report` directory.

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目 --output report
```

The evaluator uses Windows process memory counters. Use the CPython version listed in the specification. The report includes pass counts, errors, and the timing and memory metrics measured by the original evaluator. The default command uses a temporary report directory. Original fixtures or models under `judge` supply the inputs and expected outputs.
