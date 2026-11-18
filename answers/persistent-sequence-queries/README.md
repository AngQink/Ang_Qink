# 压缩持久化序列的区间查询 / Range Queries on Compressed Persistent Sequences

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 用持久化平衡二叉绳保存序列。每个节点记录虚拟长度和区间摘要，两个子树拼接时根据左侧长度移动右侧的下标权重。区间积累中要区分全局位置与区间相对位置。
2. 通过路径复制实现裁剪、拼接和版本更新，将反转与仿射变换作为惰性标记组合。下推反转时交换子树并重新解释坐标，组合变换时保留跨子树的下标偏移。
3. 重复使用二进制倍增拼接，共享已有子树。点查询按长度下降，区间查询尽量用整棵子树的摘要。释放只从版本表移除该版本，其他版本共享的节点继续有效。运行量由树高和实际访问节点决定。

### 对照验证

参考实现见 [loom.py](reference/loom.py)。它通过了本题随附的 7 项公开测试。用 `python compare.py persistent-sequence-queries` 可在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../../questions/persistent-sequence-queries/)。

## English

### Solution

1. Use a persistent balanced binary rope. Store virtual length and range aggregates at every node. When joining two subtrees, offset the right subtree's index weights by the left subtree's length. Keep global coordinates distinct from range-relative positions.
2. Use path copying for slicing, concatenation, and version updates. Compose reversals and affine transforms lazily. Pushing a reversal swaps the children and reinterprets coordinates. Composing transforms must preserve index offsets across children.
3. Build repetitions by binary doubling with shared subtrees. Descend by length for point queries and reuse aggregate data on complete subtrees for ranges. Dropping a version removes only its table entry, leaving shared nodes alive. Work depends on tree height and the nodes visited.

### Verification

See the [reference implementation](reference/loom.py). It passed all 7 bundled public tests. Run `python compare.py persistent-sequence-queries` to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../../questions/persistent-sequence-queries/).
