# 带下界和锁定边的最小费用流 / Minimum-Cost Flow with Lower Bounds and Fixed Edges

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 先扣除每条边的下界并调整顶点供需。临时锁定将该边上下界置为同一值。用辅助源汇的最大流判断剩余需求是否都能满足。
2. 在可行流的残量图上使用费用缩放求最优值和势。零约化费用残量边形成保持总费用不变的可移动空间。某边增减可通过相反方向的残量通路补偿，再用最大流求允许变化量。
3. 按边 ID 逐个最小化并冻结，得到字典序最小最优流。区间查询分别最大化和最小化目标边，不能沿用规范化时冻结的其他边。注意负费用环、自环和固定边无残量。

### 对照验证

参考实现见 [tide.py](reference/tide.py)。它通过了本题随附的 16 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

另有 [112 项原正式评测](评测/README.md)，其中包含压力和在线交互场景（以该题裁判为准）。

## English

### Solution

1. Subtract each lower bound and adjust vertex balances. A temporary fixing sets an edge's lower and upper bounds to the same value. A max-flow instance with a super-source and super-sink tests whether the remaining balances can all be met.
2. Use cost scaling on the residual graph of a feasible flow to obtain an optimum and potentials. Zero reduced-cost residual arcs describe moves that preserve the objective. A change on one arc must be compensated by residual paths in the opposite direction. Max flow gives the permitted variation.
3. Minimize and freeze edges in ID order to obtain the lexicographically smallest optimal flow. For interval queries, maximize and minimize the target edge separately without retaining fixings introduced for canonicalization. Account for negative-cost cycles, self-loops, and fixed edges with no residual flexibility.

### Verification

See the [reference implementation](reference/tide.py). It passed all 16 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).

See the [112-case official suite](评测/README.md) for the original evaluation, including stress and interactive scenarios where applicable.
