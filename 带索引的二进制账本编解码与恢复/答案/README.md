# 带索引的二进制账本编解码与恢复 / Encoding and Recovery of an Indexed Binary Ledger

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 将文件分为头、数据块、索引和尾部。逐层验证字段边界与 CRC-32C，再解释压缩负载和记录。偏移报告应来自出错字段在文件中的实际位置，多个错误同时存在时按题面优先级选择。
2. 构建时规范化 Unicode 键，按题面排序和去重，再划分记录块。规范 LZ 编码的候选范围、并列规则、长度和标记字节共同决定输出；允许多种解码输入并不意味着编码结果可任意选择。
3. 查询利用索引定位块。恢复只接受完整有效的块前缀，再重建合法文件。合并使用与构建一致的记录冲突和规范化规则，因此同一逻辑输入应得到相同字节。

### 对照验证

参考实现见 [ledger.py](reference/ledger.py)。它通过了本题随附的 9 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

## English

### Solution

1. Separate the header, data blocks, index, and footer. Validate field bounds and CRC-32C at each layer before interpreting compressed payloads or records. Report the actual file offset of a bad field and follow the prescribed precedence when multiple errors exist.
2. Normalize Unicode keys, sort and resolve duplicates as specified, then partition records into blocks. Canonical LZ output depends on the match window, tie-break, lengths, and token bytes. Accepting multiple valid decodings does not permit arbitrary canonical encodings.
3. Use the index to locate blocks for queries. Recovery accepts the complete valid block prefix and rebuilds a valid file. Merge uses the same record conflict and canonicalization rules as build, so equivalent logical input yields the same bytes.

### Verification

See the [reference implementation](reference/ledger.py). It passed all 9 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).
