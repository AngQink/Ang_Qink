# 模环上仿射关系的构造与计数

**Construction and Counting of Affine Relations over Modular Rings**

[中文](#中文) · [English](#english)

## 中文

维护模环上的仿射关系，支持映射、相交、连接和投影。计算不同可见结果的数量及字典序最小值。

[完整中文题面](SPEC.zh-CN.md)

### 自测与判据

补全 `circuit.py` 后，在当前目录运行下列命令。题包包含 14 项公开测试。

```sh
python -B -m unittest discover -s public_tests -v
```

对每个合法输入场景，响应的字段、类型、数值及数组顺序应符合题面，退出状态和输出流也应符合约定。原题资源目标为每场景 30 秒、峰值工作集 512 MiB，在线场景单条响应目标为 5 秒。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Maintain affine relations over a modular ring under mapping, intersection, joins, and projection. Count distinct visible results and find the lexicographically smallest one.

[Full English specification](SPEC.en.md)

### Self-testing and acceptance criteria

Implement `circuit.py` and run the following from this directory. This package contains 14 public tests.

```sh
python -B -m unittest discover -s public_tests -v
```

For every valid scenario, response fields, types, values, and array ordering must match the specification, as must process exit status and output streams. The benchmark budget is 30 seconds and 512 MiB peak working set per scenario, with a five-second response budget in interactive scenarios. The public runner provides local functional checks. See the specification for the full input domain.
