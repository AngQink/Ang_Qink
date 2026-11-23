# C# 批处理分片回放的缺陷修复

**C# Batch-shard replay Repair**

## 中文

修复随附工具处理乱序重放的状态缺陷。每个键初始代、序号和余额为 0。每行输出状态、代号、最近接受的序号、余额。

| a | 输入和行为 |
| --- | --- |
| 1 | b 键，c 代号，d 序号，e 带符号增量，f 来源。c 必须等于当前代，序号相比上次以 64 为模，向前 1 至 31，新余额必须在 [0,87]。全部成立才累计余额、设置序号并返回状态 1。 |
| 2 | b 键，c 新代号，d 起始序号。仅当 c 严格大于当前代时采用新代和序号，将余额清零，状态 1。 |
| 3 | 只读查询 b，状态 2。 |

被拒绝的操作状态 0，所有状态保持原样。f 的变化不会使重传变成新事件。序号范围 [0,63]。

### 交付与运行

完成 `workspace/main.cs`。评测器构建交付物并检查实际结果。从标准输入读入六个空格分隔的十进制整数，返回每行对应的四个整数。 除各命令的附加限制外，键为 0–31，字段绝对值至多 1,000,000。全零行重置状态，输出四个 0，不同段相互独立。允许 LF 或 CRLF 及结果字段间的空白。多余输出行或标准错误诊断会失败。

运行环境为 Windows .NET Framework C# 5 compiler (csc)，判据需要 Python 3.11+。编译至多 90 秒，单批运行至多 30 秒、40,000 行。用标准库或内置功能即可完成。

在本目录运行 `python 自测/grade.py` 可检查 6 组公开用例。另附[示例输入](samples/input.txt)和[预期输出](samples/expected.txt)。

## English

Repair the bundled tool's state drift under out-of-order replay. Each key begins with epoch, sequence, and balance zero. Emit status, epoch, last accepted sequence, and balance.

| a | Input and effect |
| --- | --- |
| 1 | b key, c epoch, d sequence, e signed delta, f source. Require c to equal the current epoch, d to be forward by 1 through 31 modulo 64 relative to the last sequence, and the next balance in [0,87]. Only then update sequence and balance, status 1. |
| 2 | b key, c new epoch, d initial sequence. If c is strictly newer, set epoch and sequence, clear the balance, and return status 1. |
| 3 | Inspect key b, status 2. |

A rejection emits status 0 and preserves all state. A changed source f does not make a retry new. Sequences range from 0 to 63.

### Deliverable and evaluation

Complete `workspace/main.cs`. The evaluator builds it and checks its actual results. Read six space-separated decimal integers per line from stdin and emit four integers for each line. In addition to command-specific limits, keys range from 0 to 31 and field magnitudes are at most 1,000,000. An all-zero row resets the session and emits four zeros. LF, CRLF, and whitespace between fields are accepted. Extra rows and stderr diagnostics fail.

Use Windows .NET Framework C# 5 compiler (csc) and Python 3.11+ for the evaluator. A compilation has a 90-second limit. Each run has a 30-second limit and processes up to 40,000 rows. Standard libraries or built-ins are sufficient.

Run `python 自测/grade.py` from this directory for six public cases. See the [sample input](samples/input.txt) and [expected output](samples/expected.txt).
