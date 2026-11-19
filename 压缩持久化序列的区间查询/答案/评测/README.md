# 正式评测 / Official Evaluation

## 中文

本目录包含原裁判的 57 项正式用例。`题目/public_tests` 是另一套快速自测，两个数字采用各自的统计口径。

在当前这道题的目录运行以下命令。第一条使用随附参考实现。第二条评测你在 `题目` 中完成的实现，并在新建的 `report` 目录保存逐项结果。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目 --output report
```

裁判使用 Windows 的进程内存统计，建议使用题面中的 CPython 版本。报告记录实际通过数、错误及原裁判支持的耗时和内存指标。直接运行时，报告存放在自动清理的临时目录。输入与预期结果由 `judge` 中的原用例文件或模型生成。

## English

This is the original 57-case evaluation suite. The quick tests in `题目/public_tests` are a separate suite and use a different counting convention.

Run these commands from this problem's directory. The first uses the bundled reference. The second evaluates your implementation in `题目` and writes the per-case report to a new `report` directory.

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目 --output report
```

The evaluator uses Windows process memory counters. Use the CPython version listed in the specification. The report includes pass counts, errors, and the timing and memory metrics measured by the original evaluator. The default command uses a temporary report directory. Original fixtures or models under `judge` supply the inputs and expected outputs.
