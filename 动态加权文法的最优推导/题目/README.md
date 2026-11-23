# 动态加权文法的最优推导

**Optimal Derivations in a Dynamic Weighted Grammar**

[中文](#中文) · [English](#english)

## 中文

维护可更新的加权上下文无关文法。对目标词求最小推导代价、最优推导数量或无穷性，以及规范见证。

[完整中文题面](SPEC.zh-CN.md)

### 自测与判据

补全 `ink.py` 后，在当前目录运行下列命令。题包包含 15 项公开测试。

```sh
python -B -m unittest discover -s public_tests -v
```

对每个合法输入场景，响应的字段、类型、数值及数组顺序应符合题面，退出状态和输出流也应符合约定。原题资源目标为每场景 60 秒、峰值工作集 512 MiB，在线场景单条响应目标为 5 秒。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Maintain a weighted context-free grammar under updates. For a target word, find the minimum derivation cost, count or detect infinitely many optimal derivations, and produce a canonical witness.

[Full English specification](SPEC.en.md)

### Self-testing and acceptance criteria

Implement `ink.py` and run the following from this directory. This package contains 15 public tests.

```sh
python -B -m unittest discover -s public_tests -v
```

For every valid scenario, response fields, types, values, and array ordering must match the specification, as must process exit status and output streams. The benchmark budget is 60 seconds and 512 MiB peak working set per scenario, with a five-second response budget in interactive scenarios. The public runner provides local functional checks. See the specification for the full input domain.
