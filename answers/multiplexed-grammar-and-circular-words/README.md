# 多协议命令流中的文法推导与两类环形词计数 / Grammar Derivations and Two Circular Word Counting Models in a Multiplexed Stream

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 流式分派保留三个独立状态机，分别处理固定边重数环形词、最优文法推导及带权环形词。初始化、保存、恢复与缓存失效只影响收到命令的模块。
2. 固定边重数的计数用矩阵树行列式与欧拉通路公式。加权文法用区间图表求最优代价与规范见证。带权环形词用多项式转移矩阵与群计数求旋转、反射及周期分类。两种环形词状态既不共享图也不共享余数模数。
3. 将前缀查询、文法快照加载和带权环形词边更新交错运行。在一次 `init` 后重跑其他模块的同一查询，结果应保持一致。

### 对照验证

参考实现见 [triplex.py](reference/triplex.py)。它通过了本题随附的 6 项公开测试。用 `python compare.py multiplexed-grammar-and-circular-words` 可在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../../questions/multiplexed-grammar-and-circular-words/)。

## English

### Solution

1. Dispatch the stream to three independent state machines for prescribed-edge circular words, optimal grammar derivations, and weighted circular words. Initialization, save, load, and cache invalidation affect only the addressed module.
2. Count prescribed-edge words using matrix-tree determinants and an Euler-trail formula. Use a span chart for minimum-cost grammar derivations and canonical witnesses. Use a polynomial transfer matrix and group counting for weighted-word rotations, reflections, and periods. The two circular-word states share neither graph nor residue modulus.
3. Interleave prefix queries, grammar snapshot loads, and weighted-word edge updates. After reinitializing one module, repeating an unchanged query in another module should give the same result.

### Verification

See the [reference implementation](reference/triplex.py). It passed all 6 bundled public tests. Run `python compare.py multiplexed-grammar-and-circular-words` to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../../questions/multiplexed-grammar-and-circular-words/).
