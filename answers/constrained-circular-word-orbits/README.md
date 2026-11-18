# 带权环形词的旋转与反射轨道计数 / Rotation and Reflection Orbit Counts for Weighted Circular Words

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 将颜色转移写成多项式矩阵，指数记录权重余数，在循环多项式环中用矩阵幂计算闭游走。对周期为 d 的候选块按重复次数换算原长度的目标余数。
2. 旋转不动词按 gcd 归到周期约束。对反射，需要按轴类型和颜色对合分别约束固定点与成对点；折叠环只沿半段转移。用 Burnside 计数轨道，用 Möbius 反演得到精确周期。
3. 除以群阶必须作为整数除法处理。用扩大的计数模数保留足够的信息，避免对合数模数下的不可逆因子取逆。矩阵幂的成本随长度仅对数增长，轴分类及因子枚举另计。

### 对照验证

参考实现见 [mirror.py](reference/mirror.py)。它通过了本题随附的 16 项公开测试。用 `python compare.py constrained-circular-word-orbits` 可在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../../questions/constrained-circular-word-orbits/)。

## English

### Solution

1. Use a polynomial transfer matrix whose exponents track weight residues. Matrix powers over a cyclic polynomial ring count closed walks. For a candidate block of period d, convert its weight residue using the number of repeats to test the full-length target.
2. Group rotation-fixed words by the period restriction determined by the gcd. For reflections, enforce separate conditions for fixed and paired positions according to the axis type and color involution. Count transitions on the folded half-cycle. Apply Burnside's lemma for orbits and Möbius inversion for exact periods.
3. Treat division by the group order as integer division. Working modulo a suitable multiple preserves enough information when the divisor is not invertible modulo the target modulus. Matrix exponentiation is logarithmic in word length, with additional work for axis classes and divisor enumeration.

### Verification

See the [reference implementation](reference/mirror.py). It passed all 16 bundled public tests. Run `python compare.py constrained-circular-word-orbits` to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../../questions/constrained-circular-word-orbits/).
