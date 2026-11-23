# Lua 脚本部署缓存的增量校验

**Lua Script deployment cache Incremental Validation**

## 中文

生成增量构建决策并处理延迟成功回执。每个目标初始无声明、无回执。输出状态、声明凭证、ABI 凭证、是否命中。空凭证为 0。

| a | 行为 |
| --- | --- |
| 1 | 声明目标 b，c 源码修订，d 依赖修订，e 配置，f 工具链修订，均非负。凭证为 `(c×49+d×32+e×7+f+36) mod 4093+1`、`(d×22+f×10+e×23) mod 1297+1`。保留旧回执。命中为状态 2，否则状态 3。 |
| 2 | b 收到成功回执 (c,d)。只有与当前非空声明完全一致才记录，状态 1。 |
| 3 | 吊销 b 的成功回执。只有 (c,d) 与保存回执完全一致才删除，状态 1。 |
| 4 | 请求计划。无声明为 0，命中为 2，需构建为 3。 |

拒绝确认或吊销为状态 0。是否命中始终按两项凭证都相同且有声明来判断。

### 交付与运行

完成 `workspace/main.lua`。评测器构建交付物并检查实际结果。从标准输入读入六个空格分隔的十进制整数，返回每行对应的四个整数。 除各命令的附加限制外，键为 0–31，字段绝对值至多 1,000,000。全零行重置状态，输出四个 0，不同段相互独立。允许 LF 或 CRLF 及结果字段间的空白。多余输出行或标准错误诊断会失败。

运行环境为 Lua 5.1 (PATH or BENCH_LUA)，判据需要 Python 3.11+。编译至多 90 秒，单批运行至多 30 秒、40,000 行。用标准库或内置功能即可完成。

在本目录运行 `python 自测/grade.py` 可检查 6 组公开用例。另附[示例输入](samples/input.txt)和[预期输出](samples/expected.txt)。

## English

Plan incremental work and accept late build receipts. Each target begins without a declaration or receipt. Emit status, recipe stamp, ABI stamp, and a hit bit. Missing stamps are zero.

| a | Effect |
| --- | --- |
| 1 | Declare b with source revision c, dependency revision d, profile e and tool revision f, all nonnegative. Stamps are `(c×49+d×32+e×7+f+36) mod 4093+1` and `(d×22+f×10+e×23) mod 1297+1`. Keep any previous receipt. Status 2 for hit or 3 for build. |
| 2 | Record successful receipt (c,d) only when it matches the nonempty declaration for b, status 1. |
| 3 | Revoke (c,d) only when it matches the stored receipt for b, status 1. |
| 4 | Query plan: 0 without a declaration, 2 for a hit, 3 for a build. |

Rejected acknowledgments or revocations return 0. A hit requires a declaration and both matching stamps.

### Deliverable and evaluation

Complete `workspace/main.lua`. The evaluator builds it and checks its actual results. Read six space-separated decimal integers per line from stdin and emit four integers for each line. In addition to command-specific limits, keys range from 0 to 31 and field magnitudes are at most 1,000,000. An all-zero row resets the session and emits four zeros. LF, CRLF, and whitespace between fields are accepted. Extra rows and stderr diagnostics fail.

Use Lua 5.1 (PATH or BENCH_LUA) and Python 3.11+ for the evaluator. A compilation has a 90-second limit. Each run has a 30-second limit and processes up to 40,000 rows. Standard libraries or built-ins are sufficient.

Run `python 自测/grade.py` from this directory for six public cases. See the [sample input](samples/input.txt) and [expected output](samples/expected.txt).
