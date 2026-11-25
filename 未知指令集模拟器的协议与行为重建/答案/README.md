# 未知指令集模拟器的协议与行为重建

**Protocol and Behavior Reconstruction for an Undocumented Virtual Machine**

## 当时的提交

[提交源码](reference/ghost.py)来自原对局的 ChatGPT 答案压缩包。

**公开样例通过。** 实际复跑为 **3/3** 组原始公开样例。当时的提交按一步一条指令解释指令区和寄存器状态，并单独处理陷阱、周期上限与内存摘要。每次 RUN 从 INIT 保存的初态重新开始。

从题目总目录运行以下命令可重现公开样例结果。

```powershell
python 题目/自测/grade.py --candidate 答案/reference
```

## Archived submission

The [submitted source](reference/ghost.py) is the file from the original ChatGPT contest answer archive.

**Public samples pass.** The recorded rerun is **3/3** original public samples. The submission interprets instructions against the saved initial code and register state and implements trap reporting, cycle accounting, and memory hashing. Each RUN replays from the state saved by INIT.

Run the command above from the problem directory to reproduce the public-sample result.

Submission SHA-256: `d14ecd74bb5947b8c723790ea4cf1e47c09de2e8b3351254f9539cded11f9ae7`
