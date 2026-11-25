# 数值表达式求值器的字节级兼容

**Byte-Exact Compatibility for a Numeric Expression Evaluator**

## 任务

通过随题的 Windows x64 程序 `glyph.exe` 观察原求值工具。程序从标准输入读取完整脚本，提交实现要按字节重现标准输出和标准错误，并返回相同退出码。

将实现写在 `workspace/glyph.py`。使用 Python 3.14 标准库。提交物是独立的单文件，作答时可以运行随题的 EXE 观察结果，提交的代码须自行实现行为，不能调用 EXE、DLL、外部进程或网络。

原题为 DeepSeek 对局的 **GLYPH**。本档案含原 EXE 和 5 组原始公开样例。原隐藏判据已不在留存材料中。

```powershell
python 自测/grade.py
```

公开复跑器每次将提交复制到临时目录，从样例文件读取标准输入，逐字节核对标准输出、标准错误和退出码。

## Problem

Use the supplied Windows x64 `glyph.exe` to observe the original evaluator. It reads a complete script from standard input. Reproduce stdout and stderr byte for byte, including the exit code.

Write `workspace/glyph.py` using the Python 3.14 standard library. You may run the supplied executable while investigating. Submit an independent single file that implements the behavior without calling the executable, DLLs, external processes, or network services.

DeepSeek originally issued this contest problem as **GLYPH**. The archive contains the original executable and its 5 public samples. The original hidden suite is unavailable.

```powershell
python 自测/grade.py
```

The public replay copies the submission into a temporary directory and checks its stdout, stderr, and exit code against the archived samples.

EXE SHA-256: `3de34cf08d756c9761a8dfdcdb0bff1d1d8fa783bed996308fc3cebd563dafb1`
