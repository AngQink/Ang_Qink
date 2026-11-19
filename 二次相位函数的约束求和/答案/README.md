# 二次相位函数的约束求和 / Constrained Quadratic Phase Sums

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 将二次式表示为模 4 的常数和线性系数，加上一张二次项为 2 的对称邻接位图。换元必须保留模 4 进位。例如 `a xor b = a + b - 2ab (mod 4)`，奇数系数的线性项会因此产生二次项。快照复制可变系数和邻接数据。
2. 对约束做 GF(2) 消元，按最高位选主元；零行右侧为 1 表示无解。将主元替换进二次式。将自由位设为 0，再从低位向高位求主元，得到按题目位序比较的最小可行向量。
3. 逐步对自由变量求和。奇数线性系数给出一个 `1+i` 或 `1-i` 型因子，邻居奇偶性对余式产生符号及二次项修正。偶数系数则得到倍数或奇偶约束。没有自由变量后，用 2 的平方根幂次与八次单位根指数表示结果。有可行解但振幅相消为零，与无可行解是两种不同输出。

### 对照验证

参考实现见 [phase.py](reference/phase.py)。它通过了本题随附的 13 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

## English

### Solution

1. Represent the form with a constant and linear coefficients modulo 4, plus symmetric bitsets for terms with quadratic coefficient 2. Keep modulo-4 carries during substitution. For instance, `a xor b = a + b - 2ab (mod 4)`, so an odd linear coefficient can generate a quadratic term. Clone mutable coefficients and adjacency data when saving a snapshot.
2. Eliminate constraints over GF(2), taking the highest set bit as pivot. A zero row with right-hand side 1 is infeasible. Substitute each pivot into the quadratic form. Set free bits to zero and solve pivots from low to high to obtain the lexicographically first feasible vector under the specified order.
3. Sum out free variables one at a time. An odd linear coefficient yields a factor of the form `1+i` or `1-i`, with phase and quadratic corrections determined by the parity of neighboring bits. An even coefficient yields a multiplicative factor or a parity constraint. With no free variables left, encode the result using a power of the square root of 2 and an eighth root of unity. A feasible sum can cancel to zero, which differs from infeasibility.

### Verification

See the [reference implementation](reference/phase.py). It passed all 13 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).
