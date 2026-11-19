# 动态森林的最大权独立集 / Maximum-Weight Independent Sets in Dynamic Forests

[中文](#中文) · [English](#english)

## 中文

维护带权森林，处理连边、删边和权重修改。在给定顶点取舍条件下，求最优权重并计数。

[完整中文题面](SPEC.zh-CN.md)

### 自测与判据

补全 `forest.py` 后，在当前目录运行下列命令。题包包含 8 项公开测试。

```sh
python -B -m unittest discover -s public_tests -v
```

对每个合法输入场景，响应的字段、类型、数值及数组顺序应符合题面，退出状态和输出流也应符合约定。原题资源目标为每场景 60 秒、峰值工作集 512 MiB。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Maintain a weighted forest under link, cut, and weight updates. Find and count maximum-weight independent sets subject to specified vertex-inclusion conditions.

[Full English specification](SPEC.en.md)

### Self-testing and acceptance criteria

Implement `forest.py` and run the following from this directory. This package contains 8 public tests.

```sh
python -B -m unittest discover -s public_tests -v
```

For every valid scenario, response fields, types, values, and array ordering must match the specification, as must process exit status and output streams. The benchmark budget is 60 seconds and 512 MiB peak working set per scenario. The public runner provides local functional checks. See the specification for the full input domain.
