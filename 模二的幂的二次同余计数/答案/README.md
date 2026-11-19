# 模二的幂的二次同余计数 / Counting Solutions to Quadratic Congruences Modulo Powers of Two

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 把锁定低位的变量写成 `x = a + 2^r y`，将代入造成的常数和低次项一并吸收。y 的有效位数随变量变化，恢复总计数时要校正各变量的自由提升倍数。
2. 在二次幂环上用保持可逆的替换将二次部分拆为一元块和二元块。按 2-adic 层次评估各块的指数和，用单位根正交性从特征和中提取目标同余的精确计数。
3. 见证按指定低位次序逐位固定。尝试 0 后复用计数器验证可行性，否则取 1。零多项式、域只含一个值和多重解都必须保留精确整数结果。

### 对照验证

参考实现见 [veil.py](reference/veil.py)。它通过了本题随附的 16 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

## English

### Solution

1. Write each low-bit-locked variable as `x = a + 2^r y`, adjusting the constant and lower-degree terms after substitution. The useful width of y varies by variable, so account for free lifts when recovering the total count.
2. Use invertible substitutions over the power-of-two ring to separate the quadratic part into one- and two-variable blocks. Evaluate their exponential sums by 2-adic level, then extract the exact target congruence count via orthogonality of roots of unity.
3. Construct a witness by fixing bits in the prescribed order. Try 0 and reuse the counter to test feasibility, otherwise use 1. Keep exact integers for the zero polynomial, singleton domains, and repeated solutions.

### Verification

See the [reference implementation](reference/veil.py). It passed all 16 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).
