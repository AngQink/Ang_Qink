# 双协议命令流中的文法推导与环形词计数

**Grammar Derivations and Circular Word Orbits in a Multiplexed Stream**

[中文](#中文) · [English](#english)

## 中文

在同一命令流内维护带最小节点查询的加权文法及带权环形词状态。

| 命令前缀 | 子协议 |
| --- | --- |
| `ink_` | [加权文法](protocols/optimal-and-minimum-node-derivations/SPEC.zh-CN.md) |
| `mirror_` | [带权环形词](protocols/constrained-circular-word-orbits/SPEC.zh-CN.md) |

将前缀加到子协议的原命令名上，例如 `mirror_init`。字段和应答沿用子协议题面。每个子协议维护独立的状态与快照，命令可以任意交错。本题的文法包含 `ink_minways`。

每场景至多 5,000 条命令；各查询配额为 ink_parse ≤ 32, mirror_orbit ≤ 32, ink_minways ≤ 32。两类文法查询合计至多 64 条。子协议中的“第一条命令”指对应前缀下的第一条。以本页中的组合入口、总资源及各前缀命令配额为准。

输入输出采用 UTF-8 NDJSON。读入一条命令后立即输出一条 JSON 应答并刷新，标准输出只含应答且使用 LF 换行，标准错误为空，EOF 时退出状态为 0。实现限单文件和 Python 标准库，执行时只通过标准输入输出交互。

### 自测与判据

补全 `duplex.py` 后，在当前目录运行下列命令。题包包含 8 项公开测试。

```sh
python -B -m unittest discover -s public_tests -v
```

对每个合法输入场景，响应的字段、类型、数值及数组顺序应符合题面，退出状态和输出流也应符合约定。原题资源目标为每场景 60 秒、峰值工作集 512 MiB，在线场景单条响应目标为 5 秒。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Maintain a weighted grammar with minimum-node queries and a weighted circular-word state in one command stream.

| Command prefix | Subprotocol |
| --- | --- |
| `ink_` | [Weighted grammar](protocols/optimal-and-minimum-node-derivations/SPEC.en.md) |
| `mirror_` | [Weighted circular words](protocols/constrained-circular-word-orbits/SPEC.en.md) |

Prefix each subprotocol operation with its namespace, for example `mirror_init`. Request and response fields follow the linked specification. Subprotocols maintain separate state and snapshots, and commands may be interleaved arbitrarily. This problem includes `ink_minways`.

Each scenario has at most 5,000 commands. The query limits are ink_parse ≤ 32, mirror_orbit ≤ 32, ink_minways ≤ 32. There are at most 64 grammar queries in total. A subprotocol's first command is the first command with that prefix. Use the combined entry point and quotas on this page.

Use UTF-8 NDJSON. Emit and flush one JSON response immediately after each command. Standard output contains only responses with LF line endings. Leave standard error empty and exit with status 0 at EOF. Implement a single file using the Python standard library and communicate only via standard input and output.

### Self-testing and acceptance criteria

Implement `duplex.py` and run the following from this directory. This package contains 8 public tests.

```sh
python -B -m unittest discover -s public_tests -v
```

For every valid scenario, response fields, types, values, and array ordering must match the specification, as must process exit status and output streams. The benchmark budget is 60 seconds and 512 MiB peak working set per scenario, with a five-second response budget in interactive scenarios. The public runner provides local functional checks. See the specification for the full input domain.
