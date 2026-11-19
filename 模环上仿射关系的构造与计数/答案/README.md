# 模环上仿射关系的构造与计数 / Construction and Counting of Affine Relations over Modular Rings

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 将非空关系表示为偏移量与模格生成元。加入模数倍的坐标基向量后，使用扩展欧几里得整理整数格基。仿射像与投影可直接变换偏移和生成元，再化为同样的表示。
2. 条件约束利用同余的可解性限制自由方向。交集可由对偶约束实现，连接则先做独立直积，对连接坐标施等式，最后投影。答案来自投影后的格的指数和规范代表，而不是中间变量的赋值数。
3. 模数可以合成，普通域上的逆元消元不能直接套用。零维有可能是只含空元组的集合。归约代表时必须遵循题目的坐标字典序，不能分别取各素因子分量的最小值再拼接。

### 对照验证

参考实现见 [circuit.py](reference/circuit.py)。它通过了本题随附的 14 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

## English

### Solution

1. Represent a nonempty relation by an offset and generators for a lattice of residues. Include modulus-times-coordinate directions, then use extended Euclid to reduce the integer lattice basis. Affine images and projections transform the offset and generators before reduction back to the same representation.
2. Restriction uses congruence solvability to constrain the free directions. Intersections can be expressed using dual constraints. A join starts with an independent product, enforces equality on tied coordinates, and projects. Count distinct outputs using the projected lattice index and obtain the canonical representative from that lattice.
3. The modulus can be composite, so field elimination using arbitrary inverses does not apply. A zero-dimensional relation may consist of the empty tuple. Reduce representatives in the required coordinate order rather than taking independent prime-component minima and combining them.

### Verification

See the [reference implementation](reference/circuit.py). It passed all 14 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).
