# Go 故障转移检查点的故障恢复 / Go Failover checkpoints Crash Recovery

## 中文

根据故障日志恢复各键的提交状态。每键初始已提交版本 0、值 0，无待提交记录。输出状态、已提交版本、已提交值、待提交版本（没有则 0）。

| a | 行为 |
| --- | --- |
| 1 | 为键 b 预写版本 c、值 d。仅当 c 同时大于已提交和待提交版本时覆盖待提交记录，状态 1。 |
| 2 | 确认键 b 的版本 c。c 必须匹配待提交版本且大于已提交版本。校验 d 必须等于 `(c×8+(pending_value+100)×12+b+22) mod 257`。条件均成立才原子提交、清除待提交记录，状态 1。 |
| 3 | 键 b 崩溃。只清除待提交记录，返回状态 2。 |
| 4 | 查询键 b，返回状态 3。 |

拒绝为状态 0，原状态保持。版本 0–2,000，值 −100 至 100。e、f 未用。

### 交付与运行

完成 `workspace/main.go`。评测器构建交付物并检查实际结果。从标准输入读入六个空格分隔的十进制整数，返回每行对应的四个整数。 除各命令的附加限制外，键为 0–31，字段绝对值至多 1,000,000。全零行重置状态，输出四个 0，不同段相互独立。允许 LF 或 CRLF 及结果字段间的空白。多余输出行或标准错误诊断会失败。

运行环境为 Go (PATH or BENCH_GO)，判据需要 Python 3.11+。编译至多 90 秒，单批运行至多 30 秒、40,000 行。用标准库或内置功能即可完成。

在本目录运行 `python 自测/grade.py` 可检查 6 组公开用例。另附[示例输入](samples/input.txt)和[预期输出](samples/expected.txt)。

## English

Reconstruct committed state from a fault log. Each key begins with revision 0 and value 0, with no pending entry. Emit status, committed revision, committed value, and pending revision or 0.

| a | Effect |
| --- | --- |
| 1 | Stage key b with revision c and value d. Replace pending state only when c exceeds the committed and pending revisions. Status 1. |
| 2 | Acknowledge revision c for b. It must match a pending revision newer than committed. The checksum d must equal `(c×8+(pending_value+100)×12+b+22) mod 257`. If all tests pass, commit atomically, clear pending, and return 1. |
| 3 | Crash key b, drop only pending state, status 2. |
| 4 | Inspect key b, status 3. |

Rejections have status 0 and do not change state. Revisions range from 0 to 2,000 and values from −100 to 100. Ignore e and f.

### Deliverable and evaluation

Complete `workspace/main.go`. The evaluator builds it and checks its actual results. Read six space-separated decimal integers per line from stdin and emit four integers for each line. In addition to command-specific limits, keys range from 0 to 31 and field magnitudes are at most 1,000,000. An all-zero row resets the session and emits four zeros. LF, CRLF, and whitespace between fields are accepted. Extra rows and stderr diagnostics fail.

Use Go (PATH or BENCH_GO) and Python 3.11+ for the evaluator. A compilation has a 90-second limit. Each run has a 30-second limit and processes up to 40,000 rows. Standard libraries or built-ins are sufficient.

Run `python 自测/grade.py` from this directory for six public cases. See the [sample input](samples/input.txt) and [expected output](samples/expected.txt).
