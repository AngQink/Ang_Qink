# 动态加权文法的最优推导 / Optimal Derivations in a Dynamic Weighted Grammar

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 把项目 `(A, i, j)` 表示为非终结符 A 推导目标子串 `[i,j)`。终结和空产生式给出基础项目。二元规则枚举所有切分，切分可在端点以容纳空串推导。超边非负权，按最小代价传播。
2. 从目标出发只保留达到最优代价的依赖。可达的循环可重复展开，得到无限多棵最优树。无环时按拓扑顺序累加，二元边乘两个子结果，重复规则按各自标识计数。
3. 在最优代价的边上再最小化节点数，按题目规定消解同长见证。将相同结构共享为 DAG，用整棵子树大小跳过节点以回答见证索引和摘要。主要成本取决于文法规则数和可用区间切分数。

### 对照验证

参考实现见 [ink.py](reference/ink.py)。它通过了本题随附的 15 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

另有 [72 项原正式评测](评测/README.md)，其中包含压力和在线交互场景（以该题裁判为准）。

## English

### Solution

1. Represent a chart item `(A, i, j)` as nonterminal A deriving the target substring `[i,j)`. Terminal and epsilon productions provide base items. A binary rule considers every split, including endpoints for nullable children. Propagate minimum costs on the resulting nonnegative hypergraph.
2. From the target, retain only dependencies that realize its minimum cost. A reachable cycle permits arbitrarily many optimal expansions. If the reachable graph is acyclic, accumulate counts in topological order, multiplying the child counts on binary edges and counting distinct rule identifiers separately.
3. Among minimum-cost edges, minimize witness size and apply the prescribed tie-break. Share repeated witness structures as a DAG, using subtree sizes to skip nodes for witness indexing and digests. The main cost comes from the number of rules and the available chart splits.

### Verification

See the [reference implementation](reference/ink.py). It passed all 15 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).

See the [72-case official suite](评测/README.md) for the original evaluation, including stress and interactive scenarios where applicable.
