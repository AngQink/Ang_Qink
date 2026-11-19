# 动态森林的最大权独立集 / Maximum-Weight Independent Sets in Dynamic Forests

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 树形 DP 对每个边界保留选中与未选中状态。每个值是最优权重和达到该权重的方案数。合并独立子树时权重相加、计数相乘，取最大时同权计数相加。用不可达标记区分不可能与模意义下计数为零。
2. 用链切树维护首选路径，将路径边界转移合并为矩阵，并单独记录虚子树贡献。`access` 改变首选边时，虚贡献与路径贡献都要更新。连边、删边、改权和换根都复用这套维护。
3. 查询时临时屏蔽不符合选点约束的状态，再恢复原状态。多点查询要先判断同一连通分量还是两个分量，后者独立合并。按复杂度分析应计入首选路径变更及虚贡献维护两部分。

### 对照验证

参考实现见 [forest.py](reference/forest.py)。它通过了本题随附的 8 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

## English

### Solution

1. Keep selected and unselected boundary states in a tree DP. Each stores the best weight and the number of ways to attain it. Independent merges add weights and multiply counts. Taking the maximum adds counts on ties. An unreachable marker distinguishes impossibility from a count that vanishes modulo the modulus.
2. Maintain preferred paths in a link-cut tree. Compose boundary transitions as matrices and track virtual-subtree contributions separately. When access changes a preferred edge, update both kinds of contributions. Reuse these operations for link, cut, weight changes, and rerooting.
3. For a query, temporarily disable states that violate its vertex constraints, then restore the original state. For two vertices, first distinguish a shared component from separate components. In the latter case combine the independent results. Complexity depends on both preferred-path changes and maintenance of virtual contributions.

### Verification

See the [reference implementation](reference/forest.py). It passed all 8 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).
