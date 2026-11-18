# 双协议命令流中的文法推导与环形词计数 / Grammar Derivations and Circular Word Orbits in a Multiplexed Stream

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 将一行 JSON 的命令按首个下划线切为模块前缀和子命令，只转交给对应状态机。初始化仅替换该模块，快照槽、模数和缓存都不共享。每条命令处理完立即输出并刷新。
2. 文法子系统维护区间超图。先传播最小代价，再分别统计所有最优推导与其中的最少节点推导。规范见证使用子树大小和规则顺序。环形词子系统用带权转移矩阵、反射轴折叠和因子反演得到各类轨道。
3. 对照测试时交错初始化两套协议，再用相同快照编号分别保存和恢复。组合用例同时检查 `ink_minways` 的独立答案和环形词结果。

### 对照验证

参考实现见 [duplex.py](reference/duplex.py)。它通过了本题随附的 8 项公开测试。用 `python compare.py multiplexed-grammar-and-word-orbits` 可在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../../questions/multiplexed-grammar-and-word-orbits/)。

## English

### Solution

1. Split each JSON command at the first underscore, then dispatch the operation to its own state machine. Initialization replaces only that module. Keep snapshot slots, moduli, and caches separate. Emit and flush exactly one response per command.
2. The grammar module uses a span hypergraph. Propagate minimum cost first, then count all optimal derivations and the optimal derivations with the fewest nodes separately. Use subtree sizes and rule order for canonical witnesses. The circular-word module uses weighted transfer matrices, reflection folding, and divisor inversion.
3. To test dispatch, interleave the two initializations and save and restore both with the same slot number. Combined cases check `ink_minways` independently of circular-word output.

### Verification

See the [reference implementation](reference/duplex.py). It passed all 8 bundled public tests. Run `python compare.py multiplexed-grammar-and-word-orbits` to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../../questions/multiplexed-grammar-and-word-orbits/).
