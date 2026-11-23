# 带下界和锁定边的最小费用流

**Minimum-Cost Flow with Lower Bounds and Fixed Edges**

[中文](#中文) · [English](#english)

## 中文

在带下界、容量和费用的有向网络中处理快照及临时锁定。求最小费用、规范流和各查询边在最优流中的取值区间。

[完整中文题面](SPEC.zh-CN.md)

### 自测与判据

补全 `tide.py` 后，在当前目录运行下列命令。题包包含 16 项公开测试。

```sh
python -B -m unittest discover -s public_tests -v
```

对每个合法输入场景，响应的字段、类型、数值及数组顺序应符合题面，退出状态和输出流也应符合约定。原题资源目标为每场景 60 秒、峰值工作集 512 MiB，在线场景单条响应目标为 5 秒。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Handle snapshots and temporary edge fixings in a directed network with lower bounds, capacities, and costs. Find the minimum cost, a canonical flow, and optimal-flow intervals for requested edges.

[Full English specification](SPEC.en.md)

### Self-testing and acceptance criteria

Implement `tide.py` and run the following from this directory. This package contains 16 public tests.

```sh
python -B -m unittest discover -s public_tests -v
```

For every valid scenario, response fields, types, values, and array ordering must match the specification, as must process exit status and output streams. The benchmark budget is 60 seconds and 512 MiB peak working set per scenario, with a five-second response budget in interactive scenarios. The public runner provides local functional checks. See the specification for the full input domain.
