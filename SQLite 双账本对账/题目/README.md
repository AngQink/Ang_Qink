# SQLite 双账本对账

**Reconciling Two Ledgers in SQLite**

## 中文

a=1 写入左账本，a=2 写入右账本，b 为键，c 为版本，d 为金额，e 为撤回标志（0 或 1）。a=3 对键 b 生成截至当前行的对账记录，上限版本 c。各侧独立选先前业务版本 ≤ c 的记录，按版本降序、到达顺序降序取首项。撤回与缺失都视作该侧不存在。输出位图（左存在加 1，右存在加 2）、左金额（不存在为 0）、右金额（不存在为 0）、左减右。写入输出四个 0。

### 交付与运行

完成 `workspace/main.sql`。评测器构建交付物并检查实际结果。评测器在 SQLite 中创建 `input(a,b,c,d,e,f)`，按插入次序分配 rowid。提交单条查询及其 CTE，按 rowid 输出每条输入的四列整数。 除各命令的附加限制外，键为 0–31，字段绝对值至多 1,000,000。全零行重置状态，输出四个 0，不同段相互独立。允许 LF 或 CRLF 及结果字段间的空白。多余输出行或标准错误诊断会失败。

运行环境为 SQLite 3.35+ (Python sqlite3)，判据需要 Python 3.11+。编译至多 90 秒，单批运行至多 90 秒、40,000 行。用标准库或内置功能即可完成。

在本目录运行 `python 自测/grade.py` 可检查 6 组公开用例。另附[示例输入](samples/input.txt)和[预期输出](samples/expected.txt)。

## English

Operation 1 writes the left ledger and 2 writes the right. Fields b, c, d, e are key, revision, amount and tombstone flag. Operation 3 reconciles key b at a revision ceiling c using earlier rows only. Independently choose each side's highest eligible revision, latest arrival first among ties. A tombstone makes that side absent. Output presence mask (left adds 1, right adds 2), left amount, right amount, and left minus right. Missing amounts are 0. Writes emit four zeros.

### Deliverable and evaluation

Complete `workspace/main.sql`. The evaluator builds it and checks its actual results. The evaluator creates SQLite table `input(a,b,c,d,e,f)` with rowids in insertion order. Submit one query with optional CTEs and return four integer columns per input row in rowid order. In addition to command-specific limits, keys range from 0 to 31 and field magnitudes are at most 1,000,000. An all-zero row resets the session and emits four zeros. LF, CRLF, and whitespace between fields are accepted. Extra rows and stderr diagnostics fail.

Use SQLite 3.35+ (Python sqlite3) and Python 3.11+ for the evaluator. A compilation has a 90-second limit. Each run has a 90-second limit and processes up to 40,000 rows. Standard libraries or built-ins are sufficient.

Run `python 自测/grade.py` from this directory for six public cases. See the [sample input](samples/input.txt) and [expected output](samples/expected.txt).
