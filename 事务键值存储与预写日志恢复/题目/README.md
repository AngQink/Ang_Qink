# 事务键值存储与预写日志恢复

**Transactional Key-Value Storage and Write-Ahead Log Recovery**

[中文](#中文) · [English](#english)

## 中文

实现支持多版本并发事务的键值库。按快照读取和扫描，检测提交冲突，并从可能发生撕裂写入的预写日志中恢复。

[完整中文题面](SPEC.zh-CN.md)

### 自测与判据

补全 `chronicle.py` 后，在当前目录运行下列命令。题包包含 5 项公开测试。

```sh
python -m pip install pytest
python -B -m pytest public_tests -q -p no:cacheprovider
```

应答、事务可见性、冲突结果和重启后的数据必须符合题面。部分用例还核对日志故障恢复。每个数据库进程峰值工作集上限 320 MiB，普通场景 15 秒，压力场景 25 秒。 公开脚本用于本地功能自测，完整数据范围以题面为准。

## English

Implement a multiversion transactional key-value store with snapshot reads and scans, commit-time conflict detection, and recovery from a write-ahead log that may end in a torn write.

[Full English specification](SPEC.en.md)

### Self-testing and acceptance criteria

Implement `chronicle.py` and run the following from this directory. This package contains 5 public tests.

```sh
python -m pip install pytest
python -B -m pytest public_tests -q -p no:cacheprovider
```

Responses, transaction visibility, conflicts, and state after restart must match the specification. Some cases also exercise log recovery. Each database process has a 320 MiB peak working-set limit and a 15-second budget for ordinary scenarios or 25 seconds for the stress scenario. The public runner provides local functional checks. See the specification for the full input domain.
