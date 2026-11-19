# 压缩持久化序列的区间查询 / Range Queries on Compressed Persistent Sequences

[中文](#中文) · [English](#english)

## 中文

维护支持拼接、反转、裁剪和重复的不可变序列版本。对可能极长的虚拟序列回答点值和区间摘要。

[完整中文题面](SPEC.zh-CN.md)

### 自测与判据

补全 `loom.py` 后，在当前目录运行下列命令。题包包含 7 项公开测试。

```sh
python -B -m unittest discover -s public_tests -v
```

对每个合法输入场景，响应的字段、类型、数值及数组顺序应符合题面，退出状态和输出流也应符合约定。原题资源目标为每场景 20 秒、峰值工作集 512 MiB，在线场景单条响应目标为 5 秒。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Maintain immutable sequence versions under concatenation, reversal, slicing, and repetition. Answer point and range-summary queries on potentially enormous virtual sequences.

[Full English specification](SPEC.en.md)

### Self-testing and acceptance criteria

Implement `loom.py` and run the following from this directory. This package contains 7 public tests.

```sh
python -B -m unittest discover -s public_tests -v
```

For every valid scenario, response fields, types, values, and array ordering must match the specification, as must process exit status and output streams. The benchmark budget is 20 seconds and 512 MiB peak working set per scenario, with a five-second response budget in interactive scenarios. The public runner provides local functional checks. See the specification for the full input domain.
