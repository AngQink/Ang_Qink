# 固定有向边重数的环形词计数 / Counting Circular Words with Prescribed Directed Edge Multiplicities

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 对边库存先检查平衡与有边顶点的连通条件。对可行图用有向矩阵树行列式计数根树，再用欧拉回路计数公式乘除阶乘，校正同类平行边的重复排列。
2. 周期约束将库存按重复次数成比例缩小。用约数反演与旋转群计数得到本原词及轨道。前缀固定后扣除已走边，对剩余的欧拉通路计数。构造规范词时只选择仍存在完整续接的最小颜色。
3. 阶乘商和轨道除法可能含有与模数不互素的因子。对每个素幂分开维护因子的估值和可逆部分，然后用 CRT 合并。可行性不由取模后的计数决定。

### 对照验证

参考实现见 [euler.py](reference/euler.py)。它通过了本题随附的 16 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

## English

### Solution

1. First check degree balance and connectivity on vertices incident to edges. For a feasible graph, use the directed matrix-tree determinant and multiply or divide the relevant factorials for Euler tours, accounting for indistinguishable parallel edges.
2. A period restriction scales the edge inventory by the repetition count. Divisor inversion and a rotation-group count yield primitive words and orbits. For a fixed prefix, consume its edges and count the remaining Euler trails. Construct the canonical word by choosing the least next color that still permits a complete continuation.
3. Factorial quotients and orbit division may include factors sharing primes with the modulus. Track valuations and unit factors for each prime power, then combine with CRT. A count of zero modulo the modulus does not determine feasibility.

### Verification

See the [reference implementation](reference/euler.py). It passed all 16 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).
