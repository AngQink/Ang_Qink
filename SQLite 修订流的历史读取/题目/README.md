# SQLite 修订流的历史读取

**As-of Reads over a Revision Stream**

## 中文

用 SQLite 重建带撤回记录的历史视图。每行输入形如 a b c d e f。a=1 是写记录，b 是键，c 是业务版本，d 是值，e 为撤回标志（0 或 1），f 未用。a=2 在当前位置查询键 b 的版本上限 c。仅比较此前出现、业务版本 ≤ c 的写记录，按业务版本降序、到达位置降序取一项。无记录输出 0 0 0 0。被撤回输出 2 0 版本 到达位置。其他记录输出 1 值 版本 到达位置。到达位置从会话重置行后的第一行计为 1。写记录输出四个 0。

### 交付与运行

完成 `workspace/main.sql`。评测器构建交付物并检查实际结果。评测器在 SQLite 中创建 `input(a,b,c,d,e,f)`，按插入次序分配 rowid。提交单条查询及其 CTE，按 rowid 输出每条输入的四列整数。 除各命令的附加限制外，键为 0–31，字段绝对值至多 1,000,000。全零行重置状态，输出四个 0，不同段相互独立。允许 LF 或 CRLF 及结果字段间的空白。多余输出行或标准错误诊断会失败。

运行环境为 SQLite 3.35+ (Python sqlite3)，判据需要 Python 3.11+。编译至多 90 秒，单批运行至多 90 秒、40,000 行。用标准库或内置功能即可完成。

在本目录运行 `python 自测/grade.py` 可检查 6 组公开用例。另附[示例输入](samples/input.txt)和[预期输出](samples/expected.txt)。

## English

Reconstruct an as-of SQLite view with tombstones. Rows are a b c d e f. Operation 1 writes key b, revision c, value d and deletion flag e (0 or 1), ignoring f. Operation 2 queries key b at revision ceiling c. Consider writes earlier in the same session with revision at most c, order by revision descending then arrival descending, and take one. Return 0 0 0 0 if absent, 2 0 revision arrival for a tombstone, or 1 value revision arrival. Arrival starts at 1 immediately after the session reset. Writes produce four zeros.

### Deliverable and evaluation

Complete `workspace/main.sql`. The evaluator builds it and checks its actual results. The evaluator creates SQLite table `input(a,b,c,d,e,f)` with rowids in insertion order. Submit one query with optional CTEs and return four integer columns per input row in rowid order. In addition to command-specific limits, keys range from 0 to 31 and field magnitudes are at most 1,000,000. An all-zero row resets the session and emits four zeros. LF, CRLF, and whitespace between fields are accepted. Extra rows and stderr diagnostics fail.

Use SQLite 3.35+ (Python sqlite3) and Python 3.11+ for the evaluator. A compilation has a 90-second limit. Each run has a 90-second limit and processes up to 40,000 rows. Standard libraries or built-ins are sufficient.

Run `python 自测/grade.py` from this directory for six public cases. See the [sample input](samples/input.txt) and [expected output](samples/expected.txt).
