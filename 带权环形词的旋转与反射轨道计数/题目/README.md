# 带权环形词的旋转与反射轨道计数

**Rotation and Reflection Orbit Counts for Weighted Circular Words**

[中文](#中文) · [English](#english)

## 中文

维护颜色邻接约束、权重和颜色置换。对给定长度与权重余数，统计合法环形词、旋转类、反射类及精确周期。

[完整中文题面](SPEC.zh-CN.md)

### 自测与判据

补全 `mirror.py` 后，在当前目录运行下列命令。题包包含 16 项公开测试。

```sh
python -B -m unittest discover -s public_tests -v
```

对每个合法输入场景，响应的字段、类型、数值及数组顺序应符合题面，退出状态和输出流也应符合约定。原题资源目标为每场景 60 秒、峰值工作集 512 MiB，在线场景单条响应目标为 5 秒。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Maintain color adjacency, weights, and a color involution. For a length and weight residue, count valid circular words and their rotation and reflection orbits, grouped by exact period.

[Full English specification](SPEC.en.md)

### Self-testing and acceptance criteria

Implement `mirror.py` and run the following from this directory. This package contains 16 public tests.

```sh
python -B -m unittest discover -s public_tests -v
```

For every valid scenario, response fields, types, values, and array ordering must match the specification, as must process exit status and output streams. The benchmark budget is 60 seconds and 512 MiB peak working set per scenario, with a five-second response budget in interactive scenarios. The public runner provides local functional checks. See the specification for the full input domain.
