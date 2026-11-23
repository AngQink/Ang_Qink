# SQLite 快照的跨版本父子连接 / Revision-aware Joins for SQLite Snapshots

## 中文

a=1 注册父键 b 的业务版本 c 和权重 d（e=1 表示撤回）。a=2 写入子键 b，c 是子版本，d 是父键，e 是本地值，f 未用。a=3 在子版本上限 c 查询子键 b。先在此前的子记录中按版本降序、到达降序取版本 ≤ c 的最新项。再在此前父记录中，以选中子版本为上限，查询其父键。父撤回视作缺失。输出状态码（无子=0，子存在但无可见父=1，两者都有=2）、子版本、父权重或 0、子值加父权重。两类写入输出四个 0。

### 交付与运行

完成 `workspace/main.sql`。评测器构建交付物并检查实际结果。评测器在 SQLite 中创建 `input(a,b,c,d,e,f)`，按插入次序分配 rowid。提交单条查询及其 CTE，按 rowid 输出每条输入的四列整数。 除各命令的附加限制外，键为 0–31，字段绝对值至多 1,000,000。全零行重置状态，输出四个 0，不同段相互独立。允许 LF 或 CRLF 及结果字段间的空白。多余输出行或标准错误诊断会失败。

运行环境为 SQLite 3.35+ (Python sqlite3)，判据需要 Python 3.11+。编译至多 90 秒，单批运行至多 90 秒、40,000 行。用标准库或内置功能即可完成。

在本目录运行 `python 自测/grade.py` 可检查 6 组公开用例。另附[示例输入](samples/input.txt)和[预期输出](samples/expected.txt)。

## English

Operation 1 registers parent key b at revision c with weight d. An e of 1 tombstones it. Operation 2 writes child b at revision c, pointing to parent d with local value e. Operation 3 queries child b at a revision ceiling c. First choose the latest eligible earlier child by revision then arrival. Next choose the earlier referenced parent with revision at most the selected child revision by the same ranking. A parent tombstone means absence. Output status (0 without child, 1 without a visible parent, 2 with both), child revision, parent weight or 0, and child value plus parent weight. Writes emit four zeros.

### Deliverable and evaluation

Complete `workspace/main.sql`. The evaluator builds it and checks its actual results. The evaluator creates SQLite table `input(a,b,c,d,e,f)` with rowids in insertion order. Submit one query with optional CTEs and return four integer columns per input row in rowid order. In addition to command-specific limits, keys range from 0 to 31 and field magnitudes are at most 1,000,000. An all-zero row resets the session and emits four zeros. LF, CRLF, and whitespace between fields are accepted. Extra rows and stderr diagnostics fail.

Use SQLite 3.35+ (Python sqlite3) and Python 3.11+ for the evaluator. A compilation has a 90-second limit. Each run has a 90-second limit and processes up to 40,000 rows. Standard libraries or built-ins are sufficient.

Run `python 自测/grade.py` from this directory for six public cases. See the [sample input](samples/input.txt) and [expected output](samples/expected.txt).
