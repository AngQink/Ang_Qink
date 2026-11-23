# x64 Assembly 硬件标签记录的格式兼容 / x64 Assembly Hardware tag records Format Compatibility

## 中文

兼容随附的合成旧格式。Windows x64 原生产器在 `workspace/producer.exe`，可给它发送 `1 键 类型 读数 标志 序号` 得到对应编码记录。类型 0–7，读数 −16 至 15，标志 0–3，序号 0–2,000。生产器也识别全零重置。可对照 [已知数据](samples/known.txt) 和 [编码数据](samples/encoded.txt)，再自行设计探针。

解码器收到 `1 键 字 校验值 序号 0`。字在 0–2,047，校验值在 0–250。有效记录输出 `1 类型 读数 标志`。错误校验或无效编码输出 `-1 0 0 0`，且不得改变解码状态。每个键有独立状态。`2 键 0 0 0 0` 输出四个 0，保持状态。提交的解码器须独立运行。

### 交付与运行

完成 `workspace/main.S`。评测器构建交付物并检查实际结果。从标准输入读入六个空格分隔的十进制整数，返回每行对应的四个整数。 除各命令的附加限制外，键为 0–31，字段绝对值至多 1,000,000。全零行重置状态，输出四个 0，不同段相互独立。允许 LF 或 CRLF 及结果字段间的空白。多余输出行或标准错误诊断会失败。

运行环境为 Windows x64 MinGW-w64 GCC with GNU assembler and Microsoft x64 ABI，判据需要 Python 3.11+。编译至多 90 秒，单批运行至多 30 秒、40,000 行。用标准库或内置功能即可完成。

在本目录运行 `python 自测/grade.py` 可检查 6 组公开用例。另附[示例输入](samples/input.txt)和[预期输出](samples/expected.txt)。

## English

Implement compatibility with the supplied synthetic legacy format. The Windows x64 producer is `workspace/producer.exe`. Send it `1 key kind reading flag sequence` to obtain the corresponding encoded row. Kind is 0–7, reading −16 through 15, flags 0–3, and sequence 0–2,000. The producer recognizes an all-zero reset. Start with the paired [known data](samples/known.txt) and [encoded data](samples/encoded.txt), then design your own probes.

The decoder receives `1 key word checksum sequence 0`. Words are 0–2,047 and checksums 0–250. A valid record produces `1 kind reading flag`. An invalid checksum or encoding produces `-1 0 0 0` and preserves decoding state. Each key has independent state. `2 key 0 0 0 0` emits four zeros and leaves state intact. The submitted decoder must run independently.

### Deliverable and evaluation

Complete `workspace/main.S`. The evaluator builds it and checks its actual results. Read six space-separated decimal integers per line from stdin and emit four integers for each line. In addition to command-specific limits, keys range from 0 to 31 and field magnitudes are at most 1,000,000. An all-zero row resets the session and emits four zeros. LF, CRLF, and whitespace between fields are accepted. Extra rows and stderr diagnostics fail.

Use Windows x64 MinGW-w64 GCC with GNU assembler and Microsoft x64 ABI and Python 3.11+ for the evaluator. A compilation has a 90-second limit. Each run has a 30-second limit and processes up to 40,000 rows. Standard libraries or built-ins are sufficient.

Run `python 自测/grade.py` from this directory for six public cases. See the [sample input](samples/input.txt) and [expected output](samples/expected.txt).
