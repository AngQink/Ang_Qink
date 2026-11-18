# 动态加权文法的最优推导与最小节点计数 / Optimal and Minimum-Node Derivations in a Dynamic Weighted Grammar

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 用非终结符和目标串区间作为图表项目。以代价与节点数为字典序键传播最优候选。处理产生空串的规则时，两端点都是有效切分，而且二元规则的两个相同子项仍是两个独立选择。
2. 对所有最低代价推导的计数只限制代价，故相关零代价循环可以产生无穷多棵树。最少节点计数额外限制节点数，沿该子图每步规模严格下降，可以用动态规划求有限计数。
3. 规范见证在最小代价且最小节点的候选中按规则与子树顺序选择。将见证树压缩为 DAG，大树的指定位置也可通过子树大小快速访问。模意义下计数为零时仍可能存在可行树。

### 对照验证

参考实现见 [ink.py](reference/ink.py)。它通过了本题随附的 16 项公开测试。用 `python compare.py optimal-and-minimum-node-derivations` 可在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../../questions/optimal-and-minimum-node-derivations/)。

## English

### Solution

1. Index chart items by nonterminal and target span. Propagate candidates using the lexicographic key of cost and node count. Nullable rules make both endpoint splits valid, and two identical child items still represent two independent choices.
2. Counting every minimum-cost derivation constrains only cost, so a relevant zero-cost cycle can produce infinitely many trees. The minimum-node count also constrains size. Size decreases strictly along those dependencies, permitting finite dynamic-programming counts.
3. Choose the canonical witness from the minimum-cost, minimum-node candidates using the rule and subtree order. Represent witnesses as a DAG so subtree sizes permit indexed access into very large trees. A count of zero modulo the modulus can still describe feasible trees.

### Verification

See the [reference implementation](reference/ink.py). It passed all 16 bundled public tests. Run `python compare.py optimal-and-minimum-node-derivations` to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../../questions/optimal-and-minimum-node-derivations/).
