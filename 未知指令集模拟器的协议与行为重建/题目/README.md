# 未知指令集模拟器的协议与行为重建

**Protocol and Behavior Reconstruction for an Undocumented Virtual Machine**

## 任务

通过随题的 Windows x64 模拟器 `ghost.exe` 推断其指令编码、寄存器、标志位、异常和内存哈希。输入是 UTF-8 行协议。`INIT <code_hex> <mem_hex> <r0>,...,<r15>` 保存初始状态，返回 `OK`。`RUN <max_cycles>` 从该状态重新执行，输出 `OK <halted> <trap> <pc> <cycles> <r0>,...,<r15> <memhash>`。每条响应须及时刷新。寄存器值和内存哈希使用 16 位小写十六进制。

将实现写在 `workspace/ghost.py`。使用 Python 3.14 标准库。提交物是独立的单文件，作答时可以运行随题的 EXE 观察结果，提交的代码须自行实现行为，不能调用 EXE、DLL、外部进程或网络。

原题为 DeepSeek 对局的 **GHOST-ISA**。本档案含原 EXE 和 3 组原始公开样例。原隐藏判据已不在留存材料中。

```powershell
python 自测/grade.py
```

公开复跑器每次将提交复制到临时目录，从样例文件读取标准输入，逐字节核对标准输出、标准错误和退出码。

## Problem

Probe `ghost.exe`, the supplied Windows x64 virtual-machine executable, to infer its instruction encoding, registers, flags, traps, and memory hash. Read the UTF-8 line protocol. `INIT <code_hex> <mem_hex> <r0>,...,<r15>` saves the initial state and responds `OK`. `RUN <max_cycles>` starts from that state and emits `OK <halted> <trap> <pc> <cycles> <r0>,...,<r15> <memhash>`. Flush each response as it is produced. Registers and the memory hash appear as 16 lowercase hexadecimal digits.

Write `workspace/ghost.py` using the Python 3.14 standard library. You may run the supplied executable while investigating. Submit an independent single file that implements the behavior without calling the executable, DLLs, external processes, or network services.

DeepSeek originally issued this contest problem as **GHOST-ISA**. The archive contains the original executable and its 3 public samples. The original hidden suite is unavailable.

```powershell
python 自测/grade.py
```

The public replay copies the submission into a temporary directory and checks its stdout, stderr, and exit code against the archived samples.

EXE SHA-256: `76870593a4ef1bfc6777e9ac8a72488f28687e9b494dffea84aaa56a3c029239`
