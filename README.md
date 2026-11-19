# 算法与编程自测题库 / Programming and Algorithm Benchmarks

[中文](#中文) · [English](#english) · [GitHub Releases](https://github.com/AngQink/Ang_Qink/releases/latest)

## 中文

每道题占一个顶层目录。`题目` 收录中英文题面、答题骨架、样例、公开测试和判据。`答案` 收录中英文解析、参考实现和对照脚本。

1. 在索引中选一道题，或下载它的 ZIP 并解压到独立目录。
2. 按 `题目/README.md` 作答并运行公开测试。
3. 在这道题的目录运行 `python 答案/compare.py`，用同一套测试对照参考实现。也可在仓库根目录运行 `python compare.py` 检查全套。事务键值库和二进制账本的测试需要 `pytest`。

## English

Each problem has its own top-level directory. `题目` contains the bilingual specification, starter code, examples, public tests, and acceptance criteria. `答案` contains the bilingual editorial, reference implementation, and comparison script.

1. Pick a problem from the index, or download and extract its ZIP into a separate directory.
2. Follow `题目/README.md` to implement a solution and run the public tests.
3. From the problem's directory, run `python 答案/compare.py` to check the reference implementation against the same tests. Run `python compare.py` from the repository root to check the whole collection. The transactional key-value store and indexed binary ledger require `pytest`.

## 题目索引 / Index

| 题目 / Problem | 题面 / Statement | 解析 / Editorial | 公开测试 / Public tests | 下载 / Download |
| --- | --- | --- | ---: | --- |
| 二次相位函数的约束求和 / Constrained Quadratic Phase Sums | [题目 / Problem](二次相位函数的约束求和/题目/) | [答案 / Solution](二次相位函数的约束求和/答案/) | 13 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/quadratic-phase-sums.zip) |
| 事务键值存储与预写日志恢复 / Transactional Key-Value Storage and Write-Ahead Log Recovery | [题目 / Problem](事务键值存储与预写日志恢复/题目/) | [答案 / Solution](事务键值存储与预写日志恢复/答案/) | 5 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/transactional-kv-recovery.zip) |
| 压缩持久化序列的区间查询 / Range Queries on Compressed Persistent Sequences | [题目 / Problem](压缩持久化序列的区间查询/题目/) | [答案 / Solution](压缩持久化序列的区间查询/答案/) | 7 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/persistent-sequence-queries.zip) |
| 动态森林的最大权独立集 / Maximum-Weight Independent Sets in Dynamic Forests | [题目 / Problem](动态森林的最大权独立集/题目/) | [答案 / Solution](动态森林的最大权独立集/答案/) | 8 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/dynamic-forest-independent-sets.zip) |
| 模环上仿射关系的构造与计数 / Construction and Counting of Affine Relations over Modular Rings | [题目 / Problem](模环上仿射关系的构造与计数/题目/) | [答案 / Solution](模环上仿射关系的构造与计数/答案/) | 14 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/modular-affine-relations.zip) |
| 动态加权文法的最优推导 / Optimal Derivations in a Dynamic Weighted Grammar | [题目 / Problem](动态加权文法的最优推导/题目/) | [答案 / Solution](动态加权文法的最优推导/答案/) | 15 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/optimal-weighted-derivations.zip) |
| 带权环形词的旋转与反射轨道计数 / Rotation and Reflection Orbit Counts for Weighted Circular Words | [题目 / Problem](带权环形词的旋转与反射轨道计数/题目/) | [答案 / Solution](带权环形词的旋转与反射轨道计数/答案/) | 16 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/constrained-circular-word-orbits.zip) |
| 固定有向边重数的环形词计数 / Counting Circular Words with Prescribed Directed Edge Multiplicities | [题目 / Problem](固定有向边重数的环形词计数/题目/) | [答案 / Solution](固定有向边重数的环形词计数/答案/) | 16 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/prescribed-edge-circular-words.zip) |
| 模二的幂的二次同余计数 / Counting Solutions to Quadratic Congruences Modulo Powers of Two | [题目 / Problem](模二的幂的二次同余计数/题目/) | [答案 / Solution](模二的幂的二次同余计数/答案/) | 16 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/dyadic-quadratic-congruences.zip) |
| 带下界和锁定边的最小费用流 / Minimum-Cost Flow with Lower Bounds and Fixed Edges | [题目 / Problem](带下界和锁定边的最小费用流/题目/) | [答案 / Solution](带下界和锁定边的最小费用流/答案/) | 16 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/constrained-min-cost-flow.zip) |
| 有限整数域上线性同余组的计数与排名 / Counting and Ranking Linear Congruence Solutions over Finite Integer Domains | [题目 / Problem](有限整数域上线性同余组的计数与排名/题目/) | [答案 / Solution](有限整数域上线性同余组的计数与排名/答案/) | 16 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/finite-domain-congruence-ranking.zip) |
| 最小费用有向根树的计数与排名 / Counting and Ranking Minimum-Cost Arborescences | [题目 / Problem](最小费用有向根树的计数与排名/题目/) | [答案 / Solution](最小费用有向根树的计数与排名/答案/) | 16 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/minimum-cost-arborescences.zip) |
| 带索引的二进制账本编解码与恢复 / Encoding and Recovery of an Indexed Binary Ledger | [题目 / Problem](带索引的二进制账本编解码与恢复/题目/) | [答案 / Solution](带索引的二进制账本编解码与恢复/答案/) | 9 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/binary-ledger-codec.zip) |
| 动态加权文法的最优推导与最小节点计数 / Optimal and Minimum-Node Derivations in a Dynamic Weighted Grammar | [题目 / Problem](动态加权文法的最优推导与最小节点计数/题目/) | [答案 / Solution](动态加权文法的最优推导与最小节点计数/答案/) | 16 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/optimal-and-minimum-node-derivations.zip) |
| 双协议命令流中的文法推导与环形词计数 / Grammar Derivations and Circular Word Orbits in a Multiplexed Stream | [题目 / Problem](双协议命令流中的文法推导与环形词计数/题目/) | [答案 / Solution](双协议命令流中的文法推导与环形词计数/答案/) | 8 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/multiplexed-grammar-and-word-orbits.zip) |
| 多协议命令流中的文法推导与两类环形词计数 / Grammar Derivations and Two Circular Word Counting Models in a Multiplexed Stream | [题目 / Problem](多协议命令流中的文法推导与两类环形词计数/题目/) | [答案 / Solution](多协议命令流中的文法推导与两类环形词计数/答案/) | 6 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/multiplexed-grammar-and-circular-words.zip) |
| 多协议命令流中的环形词计数与二次同余 / Circular Word Counting and Quadratic Congruences in a Multiplexed Stream | [题目 / Problem](多协议命令流中的环形词计数与二次同余/题目/) | [答案 / Solution](多协议命令流中的环形词计数与二次同余/答案/) | 6 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/multiplexed-circular-words-and-quadratic-congruences.zip) |
| 多协议命令流中的组合计数与最小费用流 / Combinatorial Counting and Minimum-Cost Flow in a Multiplexed Stream | [题目 / Problem](多协议命令流中的组合计数与最小费用流/题目/) | [答案 / Solution](多协议命令流中的组合计数与最小费用流/答案/) | 6 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/multiplexed-counting-and-min-cost-flow.zip) |
| 多协议命令流中的组合计数、最小费用流与同余排名 / Combinatorial Counting, Minimum-Cost Flow, and Congruence Ranking in a Multiplexed Stream | [题目 / Problem](多协议命令流中的组合计数、最小费用流与同余排名/题目/) | [答案 / Solution](多协议命令流中的组合计数、最小费用流与同余排名/答案/) | 7 | [ZIP](https://github.com/AngQink/Ang_Qink/releases/download/v1.1.0/multiplexed-counting-flow-and-congruence-ranking.zip) |
