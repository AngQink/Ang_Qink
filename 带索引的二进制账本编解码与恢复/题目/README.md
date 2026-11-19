# 带索引的二进制账本编解码与恢复 / Encoding and Recovery of an Indexed Binary Ledger

[中文](#中文) · [English](#english)

## 中文

实现具有块压缩、校验、索引和错误偏移报告的二进制账本工具，支持构建、查询、扫描、合并和恢复。

[完整中文题面](SPEC.zh-CN.md)

### 自测与判据

补全 `ledger.py` 后，在当前目录运行下列命令。题包包含 9 项公开测试。

```sh
python -m pip install pytest
python -B -m pytest public_tests -q -p no:cacheprovider
```

检查命令退出状态、文本输出，以及生成文件的字节内容。二进制格式、错误优先级和偏移等判据见完整题面。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Implement an indexed binary ledger with block compression, checksums, and precise error offsets. Support building, querying, scanning, merging, and recovering ledgers.

[Full English specification](SPEC.en.md)

### Self-testing and acceptance criteria

Implement `ledger.py` and run the following from this directory. This package contains 9 public tests.

```sh
python -m pip install pytest
python -B -m pytest public_tests -q -p no:cacheprovider
```

Check command exit status, text output, and the exact bytes of generated files. The full specification defines the binary format, error precedence, and reported offsets. The public runner provides local functional checks. See the specification for the full input domain.
