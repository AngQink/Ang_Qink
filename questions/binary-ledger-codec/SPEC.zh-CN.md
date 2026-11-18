# 带索引的二进制账本编解码与恢复 / Encoding and Recovery of an Indexed Binary Ledger

**规范性要求。** “必须”表示强制要求。规范形式指 `build`、`merge`、`recover` 必须生成的字节序列。

## 0. 实现、运行环境和确定性

1. 在工作目录根部编写一个自包含文件 `ledger.py`。
2. 通过 `python ledger.py <command> ...` 运行，环境为 CPython 3.14。只使用 Python 标准库，不得使用第三方包或编译扩展。
3. 仅复制 `ledger.py` 到空目录后，程序仍须可用。除指定的输入文件与自身源码外，不得读取随附数据文件。
4. 无论 Windows 控制台代码页、区域设置或 `PYTHONIOENCODING` 如何设置，标准输出一律使用 UTF-8 字节。行分隔符只用 `\n`（0x0A）。输入文件按字节流处理，其中 `.ndjson` 使用 UTF-8。
5. 相同输入必须产生完全一致的文件字节和标准输出。
6. 不联网，不启动子进程，不依赖当前目录或环境变量。

题包包含 `samples/`、`public_tests/` 和 `ledger.py` 答题骨架。

## 1. 基本编码

### 1.1 定宽整数

定宽整数均为无符号小端序，类型为 `u8`、`u16`、`u32`、`u64`。没有有符号定宽整数。

### 1.2 变长整数：无符号 LEB128

`varint` 表示 0 ≤ v < 2^64 的非负整数。以 128 为基，从最低的 7 位组开始写；每字节的 0–6 位是数据，第 7 位表示后续还有字节。编码必须用最短形式，多字节编码不得以 `0x00` 结尾。示例：`0` → `00`，`127` → `7F`，`128` → `80 01`，`300` → `AC 02`。

解码时拒绝超过 10 字节、数值超过 2^64−1 或编码不规范（如 `80 00`、`81 00`）的输入。错误为 `BAD_VARINT`，偏移按外围结构确定（第 8 节）。LZ 和索引分别用更具体的 `BAD_LZ_VARINT`、`BAD_INDEX_TRUNCATED`。

### 1.3 CRC-32C

`crc32c(data)` 使用 CRC-32C（Castagnoli）：输入和输出反射，生成多项式 0x1EDC6F41，反射形式 0x82F63B78，初值与最终异或值均为 0xFFFFFFFF。`crc32c(b"123456789") == 0xE3069283`，`crc32c(b"") == 0x00000000`。所有 CRC 字段均为该值的 32 位小端编码。

### 1.4 文本

- 键为 Unicode 字符串。使用前按 Unicode NFC（UAX #15）归一化。构建、合并、读取、扫描过滤、排序、去重均使用 NFC 形式。
- 值为 Unicode 字符串，原样保存。
- 键和值以 UTF-8 字节序列写入文件。键的长度按归一化后的字节数计算。
- 空键、空字符串值均合法。JSON `null` 表示删除标记，见第 4.2 节。

## 2. 文件布局

`.algr` 文件的布局如下。

```
+--------------------------------+ offset 0
| Header            32 bytes     |
+--------------------------------+ offset 32
| Block 0                        |   zero or more blocks, back to back
| Block 1                        |
| ...                            |
+--------------------------------+ index_offset
| Index entries                  |   one entry per block
| index_crc         4 bytes      |
+--------------------------------+ index_offset + index_len  (= file_size - 24)
| Footer            24 bytes     |
+--------------------------------+ file_size
```

`file_size = index_offset + index_len + 24`。最后一个数据块与索引之间没有额外字节，文件尾之后也没有额外字节。`index_len = len(index entries) + 4`。

## 3. 文件头（32 字节，偏移 0）

| 偏移 | 长度 | 字段 | 值或含义 |
| ---: | ---: | --- | --- |
| 0 | 8 | `magic` | 字节 `41 53 48 4C 45 44 47 31`（`"ASHLEDG1"`） |
| 8 | 2 | `version` | `u16`，值为 1 |
| 10 | 2 | `header_flags` | `u16`，值为 0 |
| 12 | 4 | `reserved` | `u32`，值为 0 |
| 16 | 8 | `record_count` | `u64`，所有数据块的记录总数 |
| 24 | 4 | `block_count` | `u32`，数据块总数 |
| 28 | 4 | `header_crc` | `u32`，`crc32c(bytes[0:28])` |

## 4. 数据块

从偏移 32 开始，数据块紧接文件头，连续存放。

### 4.1 块外层结构

令 `B` 为块的文件偏移。

| 相对偏移 | 长度 | 字段 | 值或含义 |
| ---: | ---: | --- | --- |
| +0 | 2 | `block_magic` | 字节 `42 4C`（`"BL"`） |
| +2 | 1 | `mode` | 0 为原样存储，1 为 LZ 压缩 |
| +3 | 2 | `records` | `u16`，本块记录数，至少为 1 |
| +5 | 4 | `raw_len` | `u32`，未压缩记录流的字节数 |
| +9 | 4 | `stored_len` | `u32`，`stored_payload` 的长度 |
| +13 | `stored_len` | `stored_payload` | 模式 0 保存记录流，模式 1 保存 LZ 标记流 |
| +13+`stored_len` | 4 | `block_crc` | `u32`，`crc32c(block bytes [B, B+13+stored_len))` |

块总长为 `17 + stored_len`。块之间无间隙并按键升序排列。`raw_len` 和 `stored_len` 适用 `u32` 的范围，`records` 适用 `u16` 的范围。`mode == 0` 时必须有 `stored_len == raw_len`。

### 4.2 记录流（未压缩内容）

块内按键顺序连接以下编码。

```
record := shared   u8
          flags    u8
          suffix_len  varint
          value_len   varint
          t           varint
          suffix      suffix_len bytes
          value       value_len bytes, present iff flags bit 0 == 0
```

- `flags` 第 0 位为删除标记，第 1–7 位必须为 0。删除标记的 `value_len` 必为 0，且不含值字节。普通记录的长度可为 0，但必须紧跟长度对应的值字节。
- `shared` 表示与同一块上一键的共有字节前缀长度，最大为 255。首条记录的 `shared` 必为 0。它不得大于上一键的字节长度。当前键由 `previous key bytes[0:shared] + suffix` 得到，块内首键仅为 `suffix`。
- `suffix_len = len(suffix)`，`value_len = len(value bytes)`，`t` 为时间戳。
- 键必须是合法 UTF-8，等于自身的 NFC 归一形，长度不超过 4096 字节。值须为合法 UTF-8，且不超过 1048576 字节。`0 <= t < 2^53`。
- 全文件的键按无符号字节字典序严格递增，跨块也适用。禁止重复键。`""` 是合法键，且排序最前。
- 必须解出恰好 `records` 条完整记录，并恰好消费 `raw_len` 字节。解压后多出的字节为错误。

空值与删除标记的 `value_len` 都为 0，不跟值字节。删除标记额外设置 `flags` 第 0 位。

一条记录按以下严格顺序解码并报告错误。

1. 缺少 `shared` 或 `flags` 字节时报告 `RECORD_TRUNCATED`。
2. 依次解码 `suffix_len`、`value_len`、`t`。字段尚未解完而负载结束时报告 `RECORD_TRUNCATED`。编码不规范或数值超过 `u64` 时报告 `BAD_VARINT`。
3. 检查变长字段是否完整。第 0 位为 0 时须有 `suffix_len + value_len` 字节，为 1 时只需 `suffix_len`。字节不足为 `RECORD_TRUNCATED`。
4. 检查标志位。第 1–7 位任一置位，或删除标记的 `value_len != 0`，均为 `BAD_RECORD_FLAGS`。
5. `shared > len(previous key bytes)` 为 `BAD_SHARED`，这也约束块内首条的 `shared == 0`。
6. 拼出键字节。UTF-8 非法为 `BAD_KEY_UTF8`，不等于自身的 NFC 形式为 `BAD_KEY_NFC`，超过 4096 字节为 `BAD_LIMIT`。
7. `t >= 2^53` 为 `BAD_T`。
8. 对普通记录，`value_len > 1048576` 为 `BAD_LIMIT`，值的 UTF-8 非法为 `BAD_VALUE_UTF8`。
9. 当前键须严格大于上一条记录的键。若当前记录在块首，则与前一块的最后键比较。不满足时报告 `KEY_NOT_ASCENDING`。

### 4.3 模式 1 的 LZ 标记流

`stored_payload` 解码为记录流。标记如下。

```
token := 0x00  varint(literal_len)  literal_len bytes      # literal run, literal_len >= 1
       | 0x01  varint(offset)  varint(match_len)           # back-reference, match_len >= 4
```

依次执行以下检查。

1. 输出已经恰好达到 `raw_len` 时结束。仍有存储字节则报告 `BAD_LZ_TRAILING`。
2. 输出不足 `raw_len` 且存储字节已用尽时报告 `BAD_LZ_TRUNCATED`。
3. 取出一个标记字节。
4. `0x00`：读取 `literal_len`。变长字段未读完为 `BAD_LZ_TRUNCATED`，不规范或超范围为 `BAD_LZ_VARINT`。依次检查 `literal_len < 1`（`BAD_LZ_LITERAL`）、`len(output) + literal_len > raw_len`（`BAD_LZ_SIZE`）、剩余存储字节不足 `literal_len`（`BAD_LZ_TRUNCATED`）。随后原样追加这些字节。
5. `0x01`：依次读 `offset`、`match_len`，变长字段的错误同第 4 步。依次检查 `offset < 1` 或 `offset > len(output)`（`BAD_LZ_MATCH`）、`match_len < 4`（`BAD_LZ_MATCH`）、`len(output) + match_len > raw_len`（`BAD_LZ_SIZE`）。从输出尾部往前 `offset` 字节处开始逐字节复制 `match_len` 字节，允许读写重叠。
6. 其他标记均为 `BAD_LZ_TOKEN`。完成一个标记后从第 1 步继续。

### 4.4 规范 LZ 编码

令 `R` 为未压缩记录流，`N = len(R)`。`build`、`merge` 和 `recover` 产生的压缩字节须遵循以下算法。候选位置取相同 4 字节前缀的最近 8 个位置，按由近及远检查。匹配长度上限为 65535，允许重叠。长度并列时取偏移最小者。

```
out = bytearray(); pos = 0; lit_start = 0
# candidate index: for every 4-byte prefix, remember the most recent positions where it occurs.
# Before searching at position pos, the candidate lists contain every q < pos with q+4 <= N.
while pos < N:
    best = none
    if pos + 4 <= N:
        qs = positions q with q < pos, q+4 <= N, R[q:q+4] == R[pos:pos+4]   # conceptually
        qs = the 8 greatest such q (fewer if not available)
        for q in qs (descending, i.e. nearest first):
            L = largest L with 4 <= L <= min(65535, N-pos) and R[q+i] == R[pos+i] for all i < L
            # note: q+i may be >= pos; overlapping is allowed because R is fully known
            if L is greater than current best L: best = (q, L)
            # ties keep the earliest examined = greatest q = smallest offset
    if best exists:
        if pos > lit_start: emit token 0x00, varint(pos-lit_start), R[lit_start:pos]
        emit token 0x01, varint(pos-q), varint(L)
        pos = pos + L; lit_start = pos
    else:
        pos = pos + 1
if lit_start < N: emit token 0x00, varint(N-lit_start), R[lit_start:N]
```

计算规范标记流 `T`。若 `len(T) < N`，选 `mode = 1`、`stored_len = len(T)` 和 `stored_payload = T`。否则（包括相等）选 `mode = 0`、`stored_len = raw_len` 和 `stored_payload = R`。

### 4.5 规范分块

对已排序和去重的记录依下式分块。若待追加记录使非空块的未压缩长度超过 8192，则先结束当前块，并将该记录作为下一块首条重新编码。单条记录自己超过 8192 时独占一块。没有记录时不产生数据块。

```
cur = []; cur_payload = b""; prev_key = b""
for record in sorted records:
    enc = encode_record(record, shared = (0 if cur is empty else min(255, common_prefix(prev_key, record.key_bytes))))
    if cur is not empty and len(cur_payload) + len(enc) > 8192:
        flush cur as a block
        cur = []; cur_payload = b""; prev_key = b""
        enc = encode_record(record, shared = 0)
    append record to cur; cur_payload += enc; prev_key = record.key_bytes
flush cur if non-empty
```

## 5. 索引

索引紧接最后一块，起于 `index_offset`。一块对应一项，按块顺序排列，最后跟 4 字节 CRC。索引总长度为 `index_len`。

```
entry := varint(first_key_len)  first_key_bytes  u64(block_offset)
```

- `first_key` 为该块首条记录的键字节。
- `block_offset` 为该块起始字节的绝对偏移 `B`。
- 偏移严格递增，存在块时首个偏移为 32。
- `index_crc` 是所有索引项原始字节的 `crc32c`。`index_len` 是所有项字节数加 4。

## 6. 文件尾（最后 24 字节）

| 相对偏移 | 长度 | 字段 | 值或含义 |
| ---: | ---: | --- | --- |
| 0 | 8 | `index_offset` | `u64` |
| 8 | 4 | `index_len` | `u32` |
| 12 | 4 | `footer_crc` | `u32`，`crc32c(footer bytes[0:12])` |
| 16 | 8 | `footer_magic` | `41 53 48 45 4E 44 30 31`（`"ASHEND01"`） |

文件尾起于 `file_size - 24`。

## 7. 合法性

`verify` 按第 8 节顺序检查下列条件。

1. 文件头的魔数、版本、标志、保留字段和 CRC 正确。
2. 文件尾完整，魔数与 CRC 正确。`index_offset >= 32`、`index_len >= 4`，且 `index_offset + index_len == file_size - 24`。
3. 从 32 开始的零个或多个有效块恰好填满 `[32, index_offset)`。各块外层结构、CRC、负载与记录数正确。全局键严格升序，记录均满足限制。
4. `header.block_count` 等于实际块数。
5. `header.record_count` 等于各块的实际记录数之和。
6. 索引恰有 `header.block_count` 项。每项首键和块偏移与对应块一致，各项恰好占用 `index_len - 4` 字节，且 `index_crc` 正确。

合法文件可采用不同的分块方式，可以选择不压缩，也可以使用任何能正确解码的 LZ 标记流。`verify` 接受这些表示。`build`、`merge`、`recover` 的输出须逐字节符合第 4.4 和 4.5 节的规范形式。

## 8. verify 的错误、偏移和优先级

按下面的顺序检查，标准输出报告发现的第一个错误 `ERR <CODE> <offset>`，退出码为 1。文件合法时输出 `OK <record_count> <block_count>`，退出码为 0。

- 文件头错误的偏移为出错字段的文件位置。
- 文件尾错误按字段报告 `file_size-24`、`file_size-16`、`file_size-12` 或 `file_size-8`。
- 块结构、负载和记录错误以块起始偏移 `B` 报告，`BAD_BLOCK_CRC` 则使用 `B + 13 + stored_len`。
- 索引错误使用出错项起始位置，或下面明确给出的 CRC、长度偏移。文件级截断报告当前文件大小，块截断报告块起始位置。

严格检查顺序如下。

1. `file_size < 32`：`TRUNCATED_HEADER <file_size>`。
2. 依次为 `BAD_MAGIC 0`、`BAD_VERSION 8`、`BAD_HEADER_FLAGS 10`、`BAD_RESERVED 12`、`BAD_HEADER_CRC 28`。
3. `file_size < 56`：`TRUNCATED_FOOTER <file_size>`。
4. 依次检查 `BAD_FOOTER_MAGIC <file_size-8>`、`BAD_FOOTER_CRC <file_size-12>`。若 `index_offset < 32`、`index_len < 4` 或 `index_offset + index_len != file_size - 24`，则为 `BAD_INDEX_RANGE <file_size-24>`。
5. 从 `cursor = 32` 遍历到 `index_offset`。每块依次检查：
   - `cursor + 13 > index_offset`：`BAD_BLOCK_TRUNCATED <cursor>`。
   - 块魔数不等于 `42 4C`：`BAD_BLOCK_MAGIC <cursor>`。
   - `mode > 1`：`BAD_BLOCK_MODE <cursor>`。
   - `records == 0`：`BAD_BLOCK_RECORDS <cursor>`。
   - `mode == 0 and stored_len != raw_len`：`BAD_BLOCK_SIZES <cursor>`。
   - `cursor + 17 + stored_len > index_offset`：`BAD_BLOCK_TRUNCATED <cursor>`。
   - 块 CRC 不匹配：`BAD_BLOCK_CRC <cursor + 13 + stored_len>`。
   - 模式 1 按第 4.3 节解码。相应错误为 `BAD_LZ_TOKEN`、`BAD_LZ_VARINT`、`BAD_LZ_LITERAL`、`BAD_LZ_MATCH`、`BAD_LZ_SIZE`、`BAD_LZ_TRUNCATED`、`BAD_LZ_TRAILING`，偏移均用 `cursor`。输出必须恰好是 `raw_len` 字节。
   - 按第 4.2 节指定顺序解码记录。可能产生 `RECORD_TRUNCATED`、`BAD_VARINT`、`BAD_RECORD_FLAGS`、`BAD_SHARED`、`BAD_KEY_UTF8`、`BAD_KEY_NFC`、`BAD_LIMIT`、`BAD_T`、`BAD_VALUE_UTF8`、`KEY_NOT_ASCENDING`，偏移均为 `cursor`。恰好解完 `records` 后仍有负载字节时，报告 `BAD_BLOCK_TAIL <cursor>`。
   - 将 `cursor` 增加 `17 + stored_len`。
6. 文件头中的块数与第 5 步不符时报告 `BAD_BLOCK_COUNT 24`，再检查 `BAD_RECORD_COUNT 16`。
7. 按实际块表解析第 0 至 `block_count-1` 项。若在 `index_offset + index_len - 4` 前缺少键字节或 `u64`、条目被截断或任何变长字段出错，则报告 `BAD_INDEX_TRUNCATED <entry_start>`。首键或块偏移不符时报告 `BAD_INDEX_ENTRY <entry_start>`。所有条目未恰好止于 `index_offset + index_len - 4` 时报告 `BAD_INDEX_LEN <pos>`。
8. 索引校验失败时报告 `BAD_INDEX_CRC <index_offset + index_len - 4>`。

## 9. 命令、输出格式和退出码

调用方式为 `ledger.py <command> ...`。本节输出均写到 stdout，采用 UTF-8。stderr 无强制格式，通常保持为空。退出码分别为 0 成功、1 校验失败、2 账本格式错误、3 参数错误、4 输入数据错误、5 I/O 错误。

任一命令不能读写所需文件时（包括文件不存在、权限不足等），输出 `ERR IO` 并以 5 退出。

### 9.1 build

`build <input.ndjson> <output.algr>` 读取第 10 节规定的输入，去重、排序并写入规范账本。成功时无标准输出，退出 0，创建或覆盖输出。输入数据错误时输出 `ERR INPUT <lineno> <CODE>`、退出 4，且不得创建输出或改动原有输出。写入须保证这一原子性。I/O 错误为 `ERR IO`，退出 5。

### 9.2 get

`get <file.algr> <key> [<key> ...]` 要求账本合法，否则输出 `ERR <CODE> <offset>` 并以 2 退出。按参数顺序逐键执行 NFC 归一化与查找。若该键存在且没有删除标记，输出 `json.dumps(value, ensure_ascii=False)`；否则输出 `null`。每项独占一行，恰好以一个 `\n` 结束，不加额外空格。成功退出 0。

### 9.3 scan

`scan <file.algr> [--from <key>] [--limit <n>]` 要求账本合法。格式错误时输出 `ERR <CODE> <offset>` 并以 2 退出。按键字节升序，对选中的每条记录输出：

```
json.dumps({"k": <key str>, "v": <value str or None>, "t": <t int>}, ensure_ascii=False)
```

字段恰好为 `k`、`v`、`t`，顺序如上，再接 `\n`。删除标记输出 `"v": null`。可选 `--from` 过滤掉键字节小于 NFC 归一化后的参数键字节的记录。可选 `--limit` 是非负十进制整数，限制输出条数。标志写在文件参数之后，次序可互换。成功退出 0。

### 9.4 verify

`verify <file.algr>` 按第 8 节执行。合法时输出 `OK <record_count> <block_count>`，退出 0；不合法时输出 `ERR <CODE> <offset>`，退出 1。

### 9.5 recover

`recover <input.algr> <output.algr>` 读取整个输入。`file_size < 32` 时输出 `ERR TRUNCATED_HEADER <file_size>` 并以 2 退出。魔数或版本错误时分别输出 `ERR BAD_MAGIC 0` 或 `ERR BAD_VERSION 8` 并以 2 退出。忽略文件头的 CRC、标志、保留字段及两个计数。

从偏移 32 连续尝试按第 4.1–4.2 节解块。检查外层结构、CRC、负载、记录，以及与前面已恢复的键是否保持严格升序。遇到第一个无法解码的块即停，包括文件结束、魔数不是 `"BL"` 等情况。只恢复完整合法块前缀中的记录。

按第 4.5 节重建规范账本，输出 `RECOVERED <n>`，其中 n 为恢复记录数，退出 0。只要文件头长度、魔数和版本合格，即使恢复 0 条也可成功。I/O 失败仍按本节通用规则处理。

### 9.6 merge

`merge <output.algr> <input1.algr> [<input2.algr> ...]` 要求所有输入合法。按参数顺序遇到首个不合法的输入即输出 `ERR <CODE> <offset>`，退出 2，且不得创建或修改输出。合并时同一归一化键保留 `t` 较大的记录。时间戳相等时取后一个输入文件中的记录。同一合法文件内不存在同键并列。成功时写入规范账本，无标准输出，退出 0。

### 9.7 info

`info <file.algr>` 要求账本合法，否则输出 `ERR <CODE> <offset>`，退出 2。成功时按所列字段顺序和 Python 默认分隔格式输出 `json.dumps({"records": <record_count>, "blocks": <block_count>, "bytes": <file_size>})`，再接 `\n`。

### 9.8 参数错误

未知命令、参数不足或过多、`--limit` 格式错误、未知标志均输出 `ERR USAGE`、退出 3。

## 10. build 的 NDJSON 输入

输入采用 UTF-8，按 `0x0A` 分行。每个 `0x0A` 紧邻前面的单个 `0x0D` 可去掉。不以换行结尾的最后一行仍是一行，文件尾换行不额外产生空行。每行须是恰含 `k`（字符串）、`v`（字符串或 null）与 `t`（整数）的 JSON 对象。

以下错误按序判断，行号从 1 开始，发现首个失败即输出 `ERR INPUT <lineno> <CODE>` 并以 4 退出。

- `INPUT_JSON`：不是合法 JSON 或不是对象。按 RFC 8259 严格解析，`NaN`、`Infinity`、`-Infinity` 以及无效 UTF-8 均触发此错误。
- `INPUT_SCHEMA`：字段集合不是 `{"k","v","t"}`，或成员类型不符。`t` 不接受带小数或指数的数字（如 `1.0`、`1e3`），也不接受布尔值。
- `INPUT_KEY`：键的 NFC 编码超过 4096 个 UTF-8 字节，或包含无法编码为 UTF-8 的未配对 UTF-16 代理项（如 `\ud800`）。
- `INPUT_VALUE`：值字符串超过 1048576 个 UTF-8 字节，或包含未配对代理项。
- `INPUT_T`：`t < 0` 或 `t >= 2^53`。

同一对象不允许重名字段。这种输入不纳入测试，行为未定义。按行处理并归一化键。重复键取时间戳更大的记录，时间戳相同则取较晚一行。按键的 UTF-8 字节升序写出。

## 11. 限制汇总

| 项目 | 限制 |
| --- | --- |
| NFC 后的键字节数 | ≤ 4096 |
| 值字节数 | ≤ 1048576 |
| `t` | 0 ≤ t < 2^53 |
| 每块 `records` | 1 至 65535 |
| `raw_len`、`stored_len` | `u32` |
| 规范块的未压缩负载 | ≤ 8192，单条记录本身超长时除外 |

## 12. 样例

`samples/` 中的 `input.ndjson` 和 `expected.algr` 提供逐字节的规范样例，包括空账本、小型 Unicode 账本及其扫描输出、撕裂文件及其恢复结果。其他文件按上述规则生成。同一输入两次 `build` 须得到完全一致的字节。`merge` 的输出必须等同于按第 9.6 节规则合并记录后再执行一次规范 `build`。

## 13. 规范细则（v1.2）

1. 多字节变长整数以 `0x00` 结尾即为非规范编码。第 10 字节仍有继续位或整体解码值超过 2^64−1 均非法。
2. 第 4.2 节第 2 步中，负载结束使变长整数未读完时为 `RECORD_TRUNCATED`。已经能确认非法时（需要第 11 字节，或 10 字节的数值超过 `u64`），即使负载随即结束也报 `BAD_VARINT`。
3. 第 4.2 节第 3 步只看 `flags` 第 0 位。第 1–7 位不影响检查所需的字节数。
4. 第 3 步缺值字节一律为 `RECORD_TRUNCATED`。即使 `value_len` 同时超过 1 048 576，也不报 `BAD_LIMIT` 或 `BAD_VALUE_UTF8`。
5. 第 4.4 节每次搜索 `pos` 前，候选索引含所有满足 `q < pos` 且 `q+4 <= N` 的位置，包括已编码为匹配或字面量的区段内的每个位置。
6. `BAD_INDEX_LEN <pos>` 的 `pos` 是最后一个成功解析的索引项之后、首个未消费索引字节的偏移。
7. 索引中任何变长整数错误，包括截断、非规范、超过 `u64`，一律报告起始条目偏移的 `BAD_INDEX_TRUNCATED`。
8. `--limit` 必须是单个匹配 `[0-9]+` 的 ASCII 字符串，可有前导零（`007` 表示 7）。`+3`、` 3`、`3 `、`3_0`、`0x10` 均为 `ERR USAGE`。每个标志最多出现一次，`--from=...`、`--limit=...` 和 `--` 的标志写法均非法，标志必须在文件参数之后。
9. 键、`--from` 值和 `--limit` 值按 argv 原样解释。`get f --help` 查询键 `--help`，`scan f --from -x` 用键 `-x` 过滤。空字符串参数是空键。`--` 在这些值位置没有特殊含义。
10. 开头的 UTF-8 BOM 不剥离，使第 1 行产生 `INPUT_JSON 1`。
11. 只在 CR 紧接行末 `0x0A` 时剥离 CR。末行没有换行时，其中的尾部 CR 保留，JSON 将它视作空白。空 CRLF 行（如 `...\r\n\r\n`）是空行，对应行号应报 `INPUT_JSON`。
12. 逐行错误优先级为 `INPUT_JSON`、`INPUT_SCHEMA`、`INPUT_KEY`、`INPUT_VALUE`、`INPUT_T`。按出现顺序处理行。同一行若键超长且 `t` 越界，报告 `INPUT_KEY`。
13. `ERR IO` 包括目标路径本身是目录或不能以所需模式打开的情况。`build` 写入失败时输出 `ERR IO`、退出 5，原有输出保持原样。
