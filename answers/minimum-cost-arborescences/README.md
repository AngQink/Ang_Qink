# 最小费用有向根树的计数与排名 / Counting and Ranking Minimum-Cost Arborescences

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 先从根检查有向可达性，随后对每个非根顶点减去最小入边费用。若零费用图已从根可达，剩余最优树全在零费用图中，可用有向矩阵树定理计数。
2. 否则收缩尚不可达的零费用源强连通分量。按每条入边在分量内的落点计算内部根树数量，乘进该入边的权重。保留所有费用相同的入边选择，避免只返回任选一棵最优树。
3. 通过强制或禁止边反复调用最优费用与计数求解，分别求前缀分支大小和边参与次数。排名和反查按题面的边向量顺序遍历，只接受仍达到全局最优费用的分支。

### 对照验证

参考实现见 [anchor.py](reference/anchor.py)。它通过了本题随附的 16 项公开测试。用 `python compare.py minimum-cost-arborescences` 可在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../../questions/minimum-cost-arborescences/)。

## English

### Solution

1. Check directed reachability from the root, then subtract the minimum incoming cost at each nonroot vertex. If the root reaches all vertices in the zero-cost graph, all remaining optima lie in that graph and can be counted by the directed matrix-tree theorem.
2. Otherwise contract an unreachable source strongly connected component of the zero-cost graph. Multiply each entering edge's multiplicity by the number of internal trees rooted at its endpoint. Preserve all equal-cost entry choices so the count covers every optimum.
3. Evaluate prefix branch sizes and edge participation by repeatedly solving with forced or forbidden edges. Ranking and unranking traverse the specified edge-vector order and accept only branches that retain the global minimum cost.

### Verification

See the [reference implementation](reference/anchor.py). It passed all 16 bundled public tests. Run `python compare.py minimum-cost-arborescences` to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../../questions/minimum-cost-arborescences/).
