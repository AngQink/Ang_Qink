# 多协议命令流中的组合计数、最小费用流与同余排名 / Combinatorial Counting, Minimum-Cost Flow, and Congruence Ranking in a Multiplexed Stream

[中文](#中文) · [English](#english)

## 中文

### 解析

1. 六个模块各自处理 `init`、更新、快照和查询。分派器不解释子协议的字段，只传入去掉前缀后的命令名和原始字段。
2. 线性同余模块拆分各行的素幂因子，为各变量后缀缓存列生成的像。前缀给定后扣除其贡献，通过剩余向量的可达性和纤维大小计数，再按可行前缀块执行排名和反查。
3. 公开用例 `sample_06` 专门触发新增线性同余路径。其余组合用例检查其他模块的交错执行。不同模块使用相同编号时，只从自身的状态和缓存中查询。

### 对照验证

参考实现见 [hex.py](reference/hex.py)。它通过了本题随附的 7 项公开测试。用 `python 答案/compare.py` 可从该题的目录运行，并在临时副本中复现。完整输入范围、格式和资源判据见[题目包](../题目/)。

## English

### Solution

1. Each of the six modules owns initialization, updates, snapshots, and queries. The dispatcher does not interpret the subprotocol fields. It passes along the operation without its prefix and the original fields.
2. The linear-congruence module factors row moduli into prime powers and caches the column image for each variable suffix. Subtract each fixed prefix, test whether the residual vector is reachable, and use fiber sizes to count solutions and rank or unrank by prefix blocks.
3. Public case `sample_06` specifically exercises the added linear-congruence path. The other cases exercise interleaving of the earlier modules. A module must use only its own state and cache even if another module uses the same identifier.

### Verification

See the [reference implementation](reference/hex.py). It passed all 7 bundled public tests. Run `python 答案/compare.py` from the problem directory to repeat the comparison in a temporary copy. For input bounds, output formats, and resource criteria, see the [question package](../题目/).
