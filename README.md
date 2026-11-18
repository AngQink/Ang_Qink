# 算法与编程自测题库 / Programming and Algorithm Benchmarks

[中文](#中文) · [English](#english) · [题目索引 / Index](#题目索引--index)

## 中文

这套题用于独立作答、运行测试并与参考实现对照。题目涵盖状态协议、组合计数、同余方程、图算法和存储系统。每题都有独立题面、答题骨架、公开测试及判定说明。

1. 从 [题目包](questions/) 选题，按题面实现。
2. 用每题列出的命令运行公开测试。
3. 到 [答案包](answers/) 查阅解析与参考实现。也可以在仓库根目录运行 `python compare.py`，在临时副本中用公开测试验证全部参考实现。全部运行需要先用 `python -m pip install pytest` 安装测试依赖。

## English

Use this collection to solve problems independently, run local tests, and compare your work with reference implementations. The problems cover stateful protocols, combinatorial counting, congruences, graph algorithms, and storage systems. Each problem provides a specification, starter code, public tests, and acceptance criteria.

1. Choose a problem from the [question package](questions/) and implement the specification.
2. Run the public tests using the command given with the problem.
3. Read the explanation and reference implementation in the [answer package](answers/). To run the public tests against every reference, run `python compare.py` from the repository root. Tests run in temporary copies. Install `pytest` before running the full suite.

## 题目索引 / Index

| 题目 / Problem | 公开测试 / Public tests | 解析 / Solution |
| --- | ---: | --- |
| [二次相位函数的约束求和 / Constrained Quadratic Phase Sums](questions/quadratic-phase-sums/) | [13](questions/quadratic-phase-sums/public_tests/) | [解析 / Solution](answers/quadratic-phase-sums/) |
| [事务键值存储与预写日志恢复 / Transactional Key-Value Storage and Write-Ahead Log Recovery](questions/transactional-kv-recovery/) | [5](questions/transactional-kv-recovery/public_tests/) | [解析 / Solution](answers/transactional-kv-recovery/) |
| [压缩持久化序列的区间查询 / Range Queries on Compressed Persistent Sequences](questions/persistent-sequence-queries/) | [7](questions/persistent-sequence-queries/public_tests/) | [解析 / Solution](answers/persistent-sequence-queries/) |
| [动态森林的最大权独立集 / Maximum-Weight Independent Sets in Dynamic Forests](questions/dynamic-forest-independent-sets/) | [8](questions/dynamic-forest-independent-sets/public_tests/) | [解析 / Solution](answers/dynamic-forest-independent-sets/) |
| [模环上仿射关系的构造与计数 / Construction and Counting of Affine Relations over Modular Rings](questions/modular-affine-relations/) | [14](questions/modular-affine-relations/public_tests/) | [解析 / Solution](answers/modular-affine-relations/) |
| [动态加权文法的最优推导 / Optimal Derivations in a Dynamic Weighted Grammar](questions/optimal-weighted-derivations/) | [15](questions/optimal-weighted-derivations/public_tests/) | [解析 / Solution](answers/optimal-weighted-derivations/) |
| [带权环形词的旋转与反射轨道计数 / Rotation and Reflection Orbit Counts for Weighted Circular Words](questions/constrained-circular-word-orbits/) | [16](questions/constrained-circular-word-orbits/public_tests/) | [解析 / Solution](answers/constrained-circular-word-orbits/) |
| [固定有向边重数的环形词计数 / Counting Circular Words with Prescribed Directed Edge Multiplicities](questions/prescribed-edge-circular-words/) | [16](questions/prescribed-edge-circular-words/public_tests/) | [解析 / Solution](answers/prescribed-edge-circular-words/) |
| [模二的幂的二次同余计数 / Counting Solutions to Quadratic Congruences Modulo Powers of Two](questions/dyadic-quadratic-congruences/) | [16](questions/dyadic-quadratic-congruences/public_tests/) | [解析 / Solution](answers/dyadic-quadratic-congruences/) |
| [带下界和锁定边的最小费用流 / Minimum-Cost Flow with Lower Bounds and Fixed Edges](questions/constrained-min-cost-flow/) | [16](questions/constrained-min-cost-flow/public_tests/) | [解析 / Solution](answers/constrained-min-cost-flow/) |
| [有限整数域上线性同余组的计数与排名 / Counting and Ranking Linear Congruence Solutions over Finite Integer Domains](questions/finite-domain-congruence-ranking/) | [16](questions/finite-domain-congruence-ranking/public_tests/) | [解析 / Solution](answers/finite-domain-congruence-ranking/) |
| [最小费用有向根树的计数与排名 / Counting and Ranking Minimum-Cost Arborescences](questions/minimum-cost-arborescences/) | [16](questions/minimum-cost-arborescences/public_tests/) | [解析 / Solution](answers/minimum-cost-arborescences/) |
| [带索引的二进制账本编解码与恢复 / Encoding and Recovery of an Indexed Binary Ledger](questions/binary-ledger-codec/) | [9](questions/binary-ledger-codec/public_tests/) | [解析 / Solution](answers/binary-ledger-codec/) |
| [动态加权文法的最优推导与最小节点计数 / Optimal and Minimum-Node Derivations in a Dynamic Weighted Grammar](questions/optimal-and-minimum-node-derivations/) | [16](questions/optimal-and-minimum-node-derivations/public_tests/) | [解析 / Solution](answers/optimal-and-minimum-node-derivations/) |
| [双协议命令流中的文法推导与环形词计数 / Grammar Derivations and Circular Word Orbits in a Multiplexed Stream](questions/multiplexed-grammar-and-word-orbits/) | [8](questions/multiplexed-grammar-and-word-orbits/public_tests/) | [解析 / Solution](answers/multiplexed-grammar-and-word-orbits/) |
| [多协议命令流中的文法推导与两类环形词计数 / Grammar Derivations and Two Circular Word Counting Models in a Multiplexed Stream](questions/multiplexed-grammar-and-circular-words/) | [6](questions/multiplexed-grammar-and-circular-words/public_tests/) | [解析 / Solution](answers/multiplexed-grammar-and-circular-words/) |
| [多协议命令流中的环形词计数与二次同余 / Circular Word Counting and Quadratic Congruences in a Multiplexed Stream](questions/multiplexed-circular-words-and-quadratic-congruences/) | [6](questions/multiplexed-circular-words-and-quadratic-congruences/public_tests/) | [解析 / Solution](answers/multiplexed-circular-words-and-quadratic-congruences/) |
| [多协议命令流中的组合计数与最小费用流 / Combinatorial Counting and Minimum-Cost Flow in a Multiplexed Stream](questions/multiplexed-counting-and-min-cost-flow/) | [6](questions/multiplexed-counting-and-min-cost-flow/public_tests/) | [解析 / Solution](answers/multiplexed-counting-and-min-cost-flow/) |
| [多协议命令流中的组合计数、最小费用流与同余排名 / Combinatorial Counting, Minimum-Cost Flow, and Congruence Ranking in a Multiplexed Stream](questions/multiplexed-counting-flow-and-congruence-ranking/) | [7](questions/multiplexed-counting-flow-and-congruence-ranking/public_tests/) | [解析 / Solution](answers/multiplexed-counting-flow-and-congruence-ranking/) |

## 下载 / Downloads

题目包和答案包可在 [GitHub Releases](https://github.com/AngQink/Ang_Qink/releases) 分开下载。

Download the question and answer packages separately from [GitHub Releases](https://github.com/AngQink/Ang_Qink/releases).
