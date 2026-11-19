# 二次相位函数的约束求和 / Constrained Quadratic Phase Sums

[中文](#中文) · [English](#english)

## 中文

维护定义在二元向量上的模 4 二次函数，处理变量替换和快照，并在 GF(2) 线性约束下计算精确复数和与重叠。

[完整中文题面](SPEC.zh-CN.md)

### 自测与判据

补全 `phase.py` 后，在当前目录运行下列命令。题包包含 13 项公开测试。

```sh
python -B -m unittest discover -s public_tests -v
```

对每个合法输入场景，响应的字段、类型、数值及数组顺序应符合题面，退出状态和输出流也应符合约定。原题资源目标为每场景 30 秒、峰值工作集 512 MiB，在线场景单条响应目标为 5 秒。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Maintain a quadratic function modulo 4 on binary vectors. Support variable substitutions and snapshots, and compute exact complex sums and overlaps under linear constraints over GF(2).

[Full English specification](SPEC.en.md)

### Self-testing and acceptance criteria

Implement `phase.py` and run the following from this directory. This package contains 13 public tests.

```sh
python -B -m unittest discover -s public_tests -v
```

For every valid scenario, response fields, types, values, and array ordering must match the specification, as must process exit status and output streams. The benchmark budget is 30 seconds and 512 MiB peak working set per scenario, with a five-second response budget in interactive scenarios. The public runner provides local functional checks. See the specification for the full input domain.
