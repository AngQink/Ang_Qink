# SQLite 乱序事件的会话边界 / Session Boundaries for Out-of-Order Events

## 中文

a=1 的输入表示通道 b 在时刻 c 的观测，强度为 d，e、f 未用。按同一会话内同一通道的 (c, 到达位置) 排序。第一条观测或与前一条时间差大于 8 时新开一段。对每条观测输出段号（同一通道从 1 开始）、段内观测条数、段内强度和、段的最早时间。全段使用全部输入数据，包括之后才到达的观测。最终输出顺序仍为输入顺序。

### 交付与运行

完成 `workspace/main.sql`。评测器构建交付物并检查实际结果。评测器在 SQLite 中创建 `input(a,b,c,d,e,f)`，按插入次序分配 rowid。提交单条查询及其 CTE，按 rowid 输出每条输入的四列整数。 除各命令的附加限制外，键为 0–31，字段绝对值至多 1,000,000。全零行重置状态，输出四个 0，不同段相互独立。允许 LF 或 CRLF 及结果字段间的空白。多余输出行或标准错误诊断会失败。

运行环境为 SQLite 3.35+ (Python sqlite3)，判据需要 Python 3.11+。编译至多 90 秒，单批运行至多 90 秒、40,000 行。用标准库或内置功能即可完成。

在本目录运行 `python 自测/grade.py` 可检查 6 组公开用例。另附[示例输入](samples/input.txt)和[预期输出](samples/expected.txt)。

## English

Each operation 1 is an observation on channel b at time c with intensity d. Ignore e and f. Within each reset-delimited session and channel, sort by (time, arrival). Start a new segment at the first observation or when the gap exceeds 8. For every observation emit segment number (starting at 1 per channel), segment size, sum of intensities, and earliest time. Use the entire input segment, including observations arriving later. Emit lines in original input order.

### Deliverable and evaluation

Complete `workspace/main.sql`. The evaluator builds it and checks its actual results. The evaluator creates SQLite table `input(a,b,c,d,e,f)` with rowids in insertion order. Submit one query with optional CTEs and return four integer columns per input row in rowid order. In addition to command-specific limits, keys range from 0 to 31 and field magnitudes are at most 1,000,000. An all-zero row resets the session and emits four zeros. LF, CRLF, and whitespace between fields are accepted. Extra rows and stderr diagnostics fail.

Use SQLite 3.35+ (Python sqlite3) and Python 3.11+ for the evaluator. A compilation has a 90-second limit. Each run has a 90-second limit and processes up to 40,000 rows. Standard libraries or built-ins are sufficient.

Run `python 自测/grade.py` from this directory for six public cases. See the [sample input](samples/input.txt) and [expected output](samples/expected.txt).
