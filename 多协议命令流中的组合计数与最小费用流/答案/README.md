# 多协议命令流中的组合计数与最小费用流 / Combinatorial Counting and Minimum-Cost Flow in a Multiplexed Stream

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 统一分派输入输出，五种子协议分别保存状态。前四种模块的解析和算术独立运行，并各自为代价较高的查询维护缓存。
2. 新增加的最小费用流模块先处理锁定边、下界和供需，再在可行流上做费用缩放。零约化费用残量图支持流量调整而保持费用。用它分别规范化边向量和求单边的最优取值区间。
3. 交错锁定求解、取消锁定和快照恢复。锁定只用于当前请求，规范化的逐边限制不能带到区间查询，更不能留给其他模块。

### 对照验证

参考实现见 [penta.py](reference/penta.py)。它通过了本题随附的 6 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

## English

### Solution

1. Use one dispatcher and separate state for all five protocols. The first four modules parse and compute independently, maintaining their own caches for expensive queries.
2. For the new flow module, handle fixings, lower bounds, and balances before cost-scaling a feasible flow. The zero-reduced-cost residual graph allows changes that preserve the objective. Use it to canonicalize the edge vector and to compute optimal intervals for individual edges.
3. Interleave pinned solves, unpinned solves, and snapshot restore. A pin applies only to the current request, and edge fixings used for canonicalization must not carry into interval queries or other modules.

### Verification

See the [reference implementation](reference/penta.py). It passed all 6 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).
