# 事务键值存储与预写日志恢复 / Transactional Key-Value Storage and Write-Ahead Log Recovery

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 每次事务起始记录当前提交版本。键的历史为按版本排序的值及删除标记，用二分查找快照中的可见值，并让事务自己的写入覆盖历史读。区间扫描合并自己的写集合与快照视图。
2. 提交前检查已读键、扫描区间及要写入的键是否发生题面规定的冲突。区间外的更新不能导致冲突，区间内新出现的键可能形成幻读。先写入并同步完整 WAL 帧，再发布内存状态。
3. 恢复时按顺序解析帧，验证长度、校验和、版本与事务体。只重放完整的合法前缀，按题面处理无效尾帧；删除记录仍作为版本历史。参考实现的扫描成本取决于访问的键数，点查询随该键的历史长度对数增长。

### 对照验证

参考实现见 [chronicle.py](reference/chronicle.py)。它通过了本题随附的 5 项公开测试。用 `python compare.py transactional-kv-recovery` 可在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../../questions/transactional-kv-recovery/)。

## English

### Solution

1. Record the current commit version at transaction start. Keep each key's values and tombstones in version order, then use binary search to read the snapshot, overlaying the transaction's own writes. Range scans merge the write set with the snapshot view.
2. Before committing, check read keys, scanned intervals, and written keys for the conflicts defined in the specification. An update outside a scanned range must not conflict, whereas an insertion inside the range may be a phantom. Append and sync the complete WAL frame before publishing in-memory changes.
3. During recovery, parse frames in order and validate length, checksum, version, and transaction body. Replay the longest valid prefix and handle an invalid suffix as specified. Retain deletions as versioned records. Range-scan cost depends on the number of keys visited, while point lookup is logarithmic in the key's history length.

### Verification

See the [reference implementation](reference/chronicle.py). It passed all 5 bundled public tests. Run `python compare.py transactional-kv-recovery` to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../../questions/transactional-kv-recovery/).
