"""Run public tests against one or more reference implementations."""

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
PROBLEMS = {
    "quadratic-phase-sums": "二次相位函数的约束求和",
    "transactional-kv-recovery": "事务键值存储与预写日志恢复",
    "persistent-sequence-queries": "压缩持久化序列的区间查询",
    "dynamic-forest-independent-sets": "动态森林的最大权独立集",
    "modular-affine-relations": "模环上仿射关系的构造与计数",
    "optimal-weighted-derivations": "动态加权文法的最优推导",
    "constrained-circular-word-orbits": "带权环形词的旋转与反射轨道计数",
    "prescribed-edge-circular-words": "固定有向边重数的环形词计数",
    "dyadic-quadratic-congruences": "模二的幂的二次同余计数",
    "constrained-min-cost-flow": "带下界和锁定边的最小费用流",
    "finite-domain-congruence-ranking": "有限整数域上线性同余组的计数与排名",
    "minimum-cost-arborescences": "最小费用有向根树的计数与排名",
    "binary-ledger-codec": "带索引的二进制账本编解码与恢复",
    "optimal-and-minimum-node-derivations": "动态加权文法的最优推导与最小节点计数",
    "multiplexed-grammar-and-word-orbits": "双协议命令流中的文法推导与环形词计数",
    "multiplexed-grammar-and-circular-words": "多协议命令流中的文法推导与两类环形词计数",
    "multiplexed-circular-words-and-quadratic-congruences": "多协议命令流中的环形词计数与二次同余",
    "multiplexed-counting-and-min-cost-flow": "多协议命令流中的组合计数与最小费用流",
    "multiplexed-counting-flow-and-congruence-ranking": "多协议命令流中的组合计数、最小费用流与同余排名",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", nargs="*", help="problem folder name or English slug")
    parser.add_argument("--official", action="store_true", help="run the original Windows evaluators")
    args = parser.parse_args()
    chosen = list(dict.fromkeys(PROBLEMS.get(name, name) for name in args.problem))
    relative = Path("答案") / ("评测/grade.py" if args.official else "compare.py")
    if not chosen:
        chosen = list(PROBLEMS.values())
        if args.official:
            chosen = [name for name in chosen if (ROOT / name / relative).is_file()]
        if not chosen:
            parser.error("No suites available.")
    for name in chosen:
        if name not in PROBLEMS.values():
            parser.error(f"Unknown problem: {name}")
        if not (ROOT / name / relative).is_file():
            suite = "official" if args.official else "public"
            parser.error(f"No {suite} suite available: {name}")
    failed = []
    for name in chosen:
        folder = ROOT / name
        print(f"\n[{name}]", flush=True)
        result = subprocess.run([sys.executable, "-B", str(folder / relative)], cwd=folder, check=False)
        if result.returncode:
            failed.append(name)
    print(f"\nPassed {len(chosen) - len(failed)}/{len(chosen)} problem packages.")
    for name in failed:
        print(f"FAILED {name}")
    return bool(failed)


if __name__ == "__main__":
    sys.exit(main())
