# 多协议命令流中的环形词计数与二次同余 / Circular Word Counting and Quadratic Congruences in a Multiplexed Stream

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 对每行命令拆分模块命名空间，保留四套独立状态和可重用的预计算。新增的二次同余模块不要复用环形词的计数模数，因为它的结果是精确整数。
2. 二次同余先消去锁定位，再对余下二次式做保持可逆的块分解，用指数和计数。需要见证时按题目位序逐位固定，调用计数判断是否仍可完成。其他模块沿用图表、Euler 计数、转移矩阵三套方法。
3. 特别核对多个模块同号快照与锁定位边界。返回见证前应验证它满足原式与锁定位。查询失败不得污染任一模块状态。

### 对照验证

参考实现见 [quad.py](reference/quad.py)。它通过了本题随附的 6 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

## English

### Solution

1. Split each command into namespace and operation. Maintain four independent states and their reusable preprocessing. The quadratic-congruence module returns exact integers, so it must not reuse a circular-word counting modulus.
2. Eliminate locked bits in the quadratic congruence, decompose the remaining form by invertible transformations, and count with exponential sums. For a witness, fix bits in the prescribed order and use the counter to check extendibility. The other modules retain their chart, Euler-counting, and transfer-matrix algorithms.
3. Check reused snapshot numbers across modules and boundary cases for locked bits. Validate witnesses against the original equation and locks. A failed query must not corrupt any module state.

### Verification

See the [reference implementation](reference/quad.py). It passed all 6 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).
