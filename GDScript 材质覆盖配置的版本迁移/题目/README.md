# GDScript 材质覆盖配置的版本迁移 / GDScript Material overrides Version Migration

## 中文

迁移旧数据并计算分层有效值。每键初始没有旧值，策略为继承。输出有效状态、有效值、归一化旧值、是否有旧值。缺失值用 0。

- a=1 导入 b 键旧值。c 为非负原始量，d 为启用标志（0 或 1），e 是非负来源区号。将 `c/2` 向下取整 后加 `e×22`。d 仅作为旧版兼容字段。
- a=2 设置覆盖策略。c=0 恢复继承，c=1 显式设为 d（可以为 0 或负），c=2 明确屏蔽。改变策略不更改旧值。
- a=3 查询 b。有效状态 0 缺失，1 有值，2 已屏蔽。三种操作均输出现有视图，f 未用。

### 交付与运行

完成 `workspace/main.gd`。评测器构建交付物并检查实际结果。Godot 执行脚本时，项目目录有 input.txt，每行含六个空格分隔的十进制整数。向 result.txt 写每行对应的四个整数，并关闭文件。 除各命令的附加限制外，键为 0–31，字段绝对值至多 1,000,000。全零行重置状态，输出四个 0，不同段相互独立。允许 LF 或 CRLF 及结果字段间的空白。多余输出行或标准错误诊断会失败。

运行环境为 Godot 4.x headless console (PATH or BENCH_GODOT)，判据需要 Python 3.11+。编译至多 90 秒，单批运行至多 30 秒、40,000 行。用标准库或内置功能即可完成。

在本目录运行 `python 自测/grade.py` 可检查 6 组公开用例。另附[示例输入](samples/input.txt)和[预期输出](samples/expected.txt)。

## English

Migrate legacy values and resolve layered configuration. Each key starts with no legacy value and an inherited policy. Emit effective status, effective value, normalized legacy value and its presence flag. Missing values use 0.

- a=1 imports a legacy value for b. c is a nonnegative reading, d an enabled flag (0 or 1), and e a nonnegative origin zone. Compute `c/2` rounded down, then add `e×22`. d is a legacy compatibility field and does not affect import.
- a=2 sets the policy. c=0 inherits, c=1 explicitly sets d (which may be zero or negative), and c=2 masks. Changing policy does not change the legacy value.
- a=3 queries b. Status 0 means missing, 1 present, and 2 masked. All three operations emit the same view. Ignore f.

### Deliverable and evaluation

Complete `workspace/main.gd`. The evaluator builds it and checks its actual results. When Godot runs the script, input.txt in the project root holds six space-separated decimal integers per row. Write four integers per row to result.txt and close it. In addition to command-specific limits, keys range from 0 to 31 and field magnitudes are at most 1,000,000. An all-zero row resets the session and emits four zeros. LF, CRLF, and whitespace between fields are accepted. Extra rows and stderr diagnostics fail.

Use Godot 4.x headless console (PATH or BENCH_GODOT) and Python 3.11+ for the evaluator. A compilation has a 90-second limit. Each run has a 30-second limit and processes up to 40,000 rows. Standard libraries or built-ins are sufficient.

Run `python 自测/grade.py` from this directory for six public cases. See the [sample input](samples/input.txt) and [expected output](samples/expected.txt).
