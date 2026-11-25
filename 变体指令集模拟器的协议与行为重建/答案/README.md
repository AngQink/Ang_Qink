# 变体指令集模拟器的协议与行为重建

**Protocol and Behavior Reconstruction for a Variant Virtual Machine**

## 当时的提交

[提交源码](reference/ghost.py)来自原对局的 ChatGPT 答案压缩包。

**公开样例通过。** 实际复跑为 **3/3** 组原始公开样例。当时单独为变体编写了解码与执行逻辑。提交实现保留 64 位寄存器语义，在每次 RUN 时重建设备状态，按协议输出陷阱、周期和内存摘要。

从题目总目录运行以下命令可重现公开样例结果。

```powershell
python 题目/自测/grade.py --candidate 答案/reference
```

## Archived submission

The [submitted source](reference/ghost.py) is the file from the original ChatGPT contest answer archive.

**Public samples pass.** The recorded rerun is **3/3** original public samples. The submission has its own decoder and execution semantics for this variant. It preserves 64-bit registers, reconstructs machine state for every RUN, and formats trap, cycle, and memory-hash results.

Run the command above from the problem directory to reproduce the public-sample result.

Submission SHA-256: `b1fd4ce5e1e39fe6200dd6ae44162ef76b0b6926f445d97c2292bf379286a305`
