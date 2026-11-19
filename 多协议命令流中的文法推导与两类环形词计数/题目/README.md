# 多协议命令流中的文法推导与两类环形词计数 / Grammar Derivations and Two Circular Word Counting Models in a Multiplexed Stream

[中文](#中文) · [English](#english)

## 中文

处理加权文法、固定边重数环形词和带权环形词三种独立子协议。

| 命令前缀 | 子协议 |
| --- | --- |
| `euler_` | [固定边重数的环形词](protocols/prescribed-edge-circular-words/SPEC.zh-CN.md) |
| `ink_` | [加权文法](protocols/optimal-weighted-derivations/SPEC.zh-CN.md) |
| `mirror_` | [带权环形词](protocols/constrained-circular-word-orbits/SPEC.zh-CN.md) |

将前缀加到子协议的原命令名上，例如 `mirror_init`。字段和应答沿用子协议题面。每个子协议维护独立的状态与快照，命令可以任意交错。

每场景至多 5,000 条命令；各查询配额为 euler_count ≤ 32, ink_parse ≤ 32, mirror_orbit ≤ 32。子协议中的“第一条命令”指对应前缀下的第一条。以本页中的组合入口、总资源及各前缀命令配额为准。

输入输出采用 UTF-8 NDJSON。读入一条命令后立即输出一条 JSON 应答并刷新，标准输出只含应答且使用 LF 换行，标准错误为空，EOF 时退出状态为 0。实现限单文件和 Python 标准库，执行时只通过标准输入输出交互。

### 自测与判据

补全 `triplex.py` 后，在当前目录运行下列命令。题包包含 6 项公开测试。

```sh
python -B -m unittest discover -s public_tests -v
```

对每个合法输入场景，响应的字段、类型、数值及数组顺序应符合题面，退出状态和输出流也应符合约定。原题资源目标为每场景 60 秒、峰值工作集 512 MiB，在线场景单条响应目标为 5 秒。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Handle three independent protocols for weighted grammars, circular words with prescribed edge multiplicities, and weighted circular-word orbits.

| Command prefix | Subprotocol |
| --- | --- |
| `euler_` | [Circular words with prescribed edge multiplicities](protocols/prescribed-edge-circular-words/SPEC.en.md) |
| `ink_` | [Weighted grammar](protocols/optimal-weighted-derivations/SPEC.en.md) |
| `mirror_` | [Weighted circular words](protocols/constrained-circular-word-orbits/SPEC.en.md) |

Prefix each subprotocol operation with its namespace, for example `mirror_init`. Request and response fields follow the linked specification. Subprotocols maintain separate state and snapshots, and commands may be interleaved arbitrarily.

Each scenario has at most 5,000 commands. The query limits are euler_count ≤ 32, ink_parse ≤ 32, mirror_orbit ≤ 32. A subprotocol's first command is the first command with that prefix. Use the combined entry point and quotas on this page.

Use UTF-8 NDJSON. Emit and flush one JSON response immediately after each command. Standard output contains only responses with LF line endings. Leave standard error empty and exit with status 0 at EOF. Implement a single file using the Python standard library and communicate only via standard input and output.

### Self-testing and acceptance criteria

Implement `triplex.py` and run the following from this directory. This package contains 6 public tests.

```sh
python -B -m unittest discover -s public_tests -v
```

For every valid scenario, response fields, types, values, and array ordering must match the specification, as must process exit status and output streams. The benchmark budget is 60 seconds and 512 MiB peak working set per scenario, with a five-second response budget in interactive scenarios. The public runner provides local functional checks. See the specification for the full input domain.
