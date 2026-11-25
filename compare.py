"""Run the bundled references for selected problems or languages."""

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PROBLEMS = {
    'quadratic-phase-sums': ('二次相位函数的约束求和', 'python', True),
    'transactional-kv-recovery': ('事务键值存储与预写日志恢复', 'python', True),
    'persistent-sequence-queries': ('压缩持久化序列的区间查询', 'python', True),
    'dynamic-forest-independent-sets': ('动态森林的最大权独立集', 'python', True),
    'modular-affine-relations': ('模环上仿射关系的构造与计数', 'python', True),
    'optimal-weighted-derivations': ('动态加权文法的最优推导', 'python', True),
    'constrained-circular-word-orbits': ('带权环形词的旋转与反射轨道计数', 'python', True),
    'prescribed-edge-circular-words': ('固定有向边重数的环形词计数', 'python', True),
    'dyadic-quadratic-congruences': ('模二的幂的二次同余计数', 'python', True),
    'constrained-min-cost-flow': ('带下界和锁定边的最小费用流', 'python', True),
    'finite-domain-congruence-ranking': ('有限整数域上线性同余组的计数与排名', 'python', True),
    'minimum-cost-arborescences': ('最小费用有向根树的计数与排名', 'python', True),
    'binary-ledger-codec': ('带索引的二进制账本编解码与恢复', 'python', True),
    'optimal-and-minimum-node-derivations': ('动态加权文法的最优推导与最小节点计数', 'python', True),
    'multiplexed-grammar-and-word-orbits': ('双协议命令流中的文法推导与环形词计数', 'python', True),
    'multiplexed-grammar-and-circular-words': ('多协议命令流中的文法推导与两类环形词计数', 'python', True),
    'multiplexed-circular-words-and-quadratic-congruences': ('多协议命令流中的环形词计数与二次同余', 'python', True),
    'multiplexed-counting-and-min-cost-flow': ('多协议命令流中的组合计数与最小费用流', 'python', True),
    'multiplexed-counting-flow-and-congruence-ranking': ('多协议命令流中的组合计数、最小费用流与同余排名', 'python', True),
    'python-repair': ('Python 租约事件重放的缺陷修复', 'python', False),
    'python-format': ('Python 采集端遥测的格式兼容', 'python', False),
    'python-recovery': ('Python 检查点与残缺事务日志恢复', 'python', False),
    'python-migration': ('Python 工作区配置的版本迁移', 'python', False),
    'python-build': ('Python 增量构建的增量校验', 'python', False),
    'java-repair': ('Java 消费者位点同步的缺陷修复', 'java', False),
    'java-format': ('Java 序列化指标的格式兼容', 'java', False),
    'java-recovery': ('Java 本地提交日志的故障恢复', 'java', False),
    'java-migration': ('Java 多版本 JAR 的可重复压平', 'java', False),
    'java-build': ('Java 多模块构建的增量校验', 'java', False),
    'c-repair': ('C 驱动计数器重放的缺陷修复', 'c', False),
    'c-format': ('C 设备记录的格式兼容', 'c', False),
    'c-recovery': ('C 页缓存的故障恢复', 'c', False),
    'c-migration': ('C 固件设置的版本迁移', 'c', False),
    'c-build': ('C 目标文件缓存的增量校验', 'c', False),
    'cpp-repair': ('C++ 渲染资源生命周期的缺陷修复', 'cpp', False),
    'cpp-format': ('C++ 资源包索引的格式兼容', 'cpp', False),
    'cpp-recovery': ('C++ 场景事务的故障恢复', 'cpp', False),
    'cpp-migration': ('C++ 材质参数的版本迁移', 'cpp', False),
    'cpp-build': ('C++ 双配置 CMake 构建修复', 'cpp', False),
    'rust-repair': ('Rust 任务队列确认的缺陷修复', 'rust', False),
    'rust-format': ('Rust 存储块标记的格式兼容', 'rust', False),
    'rust-recovery': ('Rust 存储快照的故障恢复', 'rust', False),
    'rust-migration': ('Rust 序列化配置的版本迁移', 'rust', False),
    'rust-build': ('Rust 本地依赖的 Cargo 特性修复', 'rust', False),
    'go-repair': ('Go 消息分区同步的缺陷修复', 'go', False),
    'go-format': ('Go 服务采样的格式兼容', 'go', False),
    'go-recovery': ('Go 故障转移检查点的故障恢复', 'go', False),
    'go-migration': ('Go 服务启动参数的版本迁移', 'go', False),
    'go-build': ('Go 分片制品的校验和重组', 'go', False),
    'javascript-repair': ('JavaScript 离线同步消息的缺陷修复', 'javascript', False),
    'javascript-format': ('JavaScript 客户端事件包的格式兼容', 'javascript', False),
    'javascript-recovery': ('JavaScript 离线草稿的故障恢复', 'javascript', False),
    'javascript-migration': ('JavaScript 插件配置的版本迁移', 'javascript', False),
    'javascript-build': ('JavaScript 前端产物缓存的增量校验', 'javascript', False),
    'typescript-repair': ('TypeScript 会话状态同步的缺陷修复', 'typescript', False),
    'typescript-format': ('TypeScript 桥接事件记录的格式兼容', 'typescript', False),
    'typescript-recovery': ('TypeScript 插件状态快照的故障恢复', 'typescript', False),
    'typescript-migration': ('TypeScript 多版本接口配置的版本迁移', 'typescript', False),
    'typescript-build': ('TypeScript 声明文件缓存的增量校验', 'typescript', False),
    'csharp-repair': ('C# 批处理分片回放的缺陷修复', 'csharp', False),
    'csharp-format': ('C# 桌面采集记录的格式兼容', 'csharp', False),
    'csharp-recovery': ('C# 文档队列日志的故障恢复', 'csharp', False),
    'csharp-migration': ('C# 部署配置的版本迁移', 'csharp', False),
    'csharp-build': ('C# 桌面包构建的增量校验', 'csharp', False),
    'vbnet-repair': ('VB.NET 文件导入批次的缺陷修复', 'vbnet', False),
    'vbnet-format': ('VB.NET 旧版设备报文的格式兼容', 'vbnet', False),
    'vbnet-recovery': ('VB.NET 报表检查点的故障恢复', 'vbnet', False),
    'vbnet-migration': ('VB.NET 报表参数的版本迁移', 'vbnet', False),
    'vbnet-build': ('VB.NET 报表生成缓存的增量校验', 'vbnet', False),
    'powershell-repair': ('PowerShell 部署事件对账的缺陷修复', 'powershell', False),
    'powershell-format': ('PowerShell 作业执行记录的格式兼容', 'powershell', False),
    'powershell-recovery': ('PowerShell 作业恢复点的故障恢复', 'powershell', False),
    'powershell-migration': ('PowerShell 层级运维配置的版本迁移', 'powershell', False),
    'powershell-build': ('PowerShell 发布文件清单的增量对账', 'powershell', False),
    'bash-repair': ('Bash 批任务增量回放的缺陷修复', 'bash', False),
    'bash-format': ('Bash 构建事件记录的格式兼容', 'bash', False),
    'bash-recovery': ('Bash 发布快照的故障恢复', 'bash', False),
    'bash-migration': ('Bash 启动脚本参数的版本迁移', 'bash', False),
    'bash-build': ('Bash 发布任务缓存的增量校验', 'bash', False),
    'perl-repair': ('Perl 采集器偏移回放的缺陷修复', 'perl', False),
    'perl-format': ('Perl 旧采集记录的格式兼容', 'perl', False),
    'perl-recovery': ('Perl 文本索引提交的故障恢复', 'perl', False),
    'perl-migration': ('Perl 目录导入规则的版本迁移', 'perl', False),
    'perl-build': ('Perl 数据处理产物的增量校验', 'perl', False),
    'awk-repair': ('GNU Awk 日志分区重放的缺陷修复', 'awk', False),
    'awk-format': ('GNU Awk 设备日志记录的格式兼容', 'awk', False),
    'awk-recovery': ('GNU Awk 日志快照索引的故障恢复', 'awk', False),
    'awk-migration': ('GNU Awk 表格导入配置的版本迁移', 'awk', False),
    'awk-build': ('GNU Awk 预处理制品缓存的增量校验', 'awk', False),
    'fortran-repair': ('Fortran 批量模拟计数器的缺陷修复', 'fortran', False),
    'fortran-format': ('Fortran 数值采样记录的格式兼容', 'fortran', False),
    'fortran-recovery': ('Fortran 求解器检查点的故障恢复', 'fortran', False),
    'fortran-migration': ('Fortran 网格运行设置的版本迁移', 'fortran', False),
    'fortran-build': ('Fortran 实验产物复用的增量校验', 'fortran', False),
    'vbs-repair': ('VBScript 旧归档任务重放的缺陷修复', 'vbs', False),
    'vbs-format': ('VBScript 归档记录头的格式兼容', 'vbs', False),
    'vbs-recovery': ('VBScript 桌面队列恢复的故障恢复', 'vbs', False),
    'vbs-migration': ('VBScript 旧客户端参数的版本迁移', 'vbs', False),
    'vbs-build': ('VBScript 离线发布缓存的增量校验', 'vbs', False),
    'batch-repair': ('Windows Batch 安装任务回执的缺陷修复', 'batch', False),
    'batch-format': ('Windows Batch 安装事件帧的格式兼容', 'batch', False),
    'batch-recovery': ('Windows Batch 作业日志边界的故障恢复', 'batch', False),
    'batch-migration': ('Windows Batch 批量部署参数的版本迁移', 'batch', False),
    'batch-build': ('Windows Batch Windows 制品计划的增量校验', 'batch', False),
    'asm-repair': ('x64 Assembly 底层计数器窗口的缺陷修复', 'asm', False),
    'asm-format': ('x64 Assembly 硬件标签记录的格式兼容', 'asm', False),
    'asm-recovery': ('x64 Assembly 记录提交边界的故障恢复', 'asm', False),
    'asm-migration': ('x64 Assembly 配置寄存器迁移的版本迁移', 'asm', False),
    'asm-build': ('x64 Assembly 低层缓存凭证的增量校验', 'asm', False),
    'cuda-repair': ('CUDA C++ 设备任务提交序列的缺陷修复', 'cuda', False),
    'cuda-format': ('CUDA C++ 核函数采样记录的格式兼容', 'cuda', False),
    'cuda-recovery': ('CUDA C++ 设备快照序列的故障恢复', 'cuda', False),
    'cuda-migration': ('CUDA C++ 计算作业参数的版本迁移', 'cuda', False),
    'cuda-build': ('CUDA C++ 内核缓存凭证的增量校验', 'cuda', False),
    'sqlite-asof-corrections': ('SQLite 修订流的历史读取', 'sql', False),
    'sqlite-session-boundaries': ('SQLite 乱序事件的会话边界', 'sql', False),
    'sqlite-two-ledger-reconciliation': ('SQLite 双账本对账', 'sql', False),
    'sqlite-effective-interval-priority': ('SQLite 重叠有效期的优先级归并', 'sql', False),
    'sqlite-parent-revision-join': ('SQLite 快照的跨版本父子连接', 'sql', False),
    'lua-repair': ('Lua 插件消息回放的缺陷修复', 'lua', False),
    'lua-format': ('Lua 插件记录包的格式兼容', 'lua', False),
    'lua-recovery': ('Lua 插件存储日志的故障恢复', 'lua', False),
    'lua-migration': ('Lua 任务配置迁移的版本迁移', 'lua', False),
    'lua-build': ('Lua 脚本部署缓存的增量校验', 'lua', False),
    'gdscript-repair': ('GDScript 场景资源事件的缺陷修复', 'gdscript', False),
    'gdscript-format': ('GDScript 编辑器遥测记录的格式兼容', 'gdscript', False),
    'gdscript-recovery': ('GDScript 场景保存检查点的故障恢复', 'gdscript', False),
    'gdscript-migration': ('GDScript 材质覆盖配置的版本迁移', 'gdscript', False),
    'gdscript-build': ('GDScript 资源导入缓存的增量校验', 'gdscript', False),
    'glyph-evaluator': ('数值表达式求值器的字节级兼容', 'python', False),
    'glyph80-evaluator': ('八十位浮点求值器的字节级兼容', 'python', False),
    'ghost-isa-emulator': ('未知指令集模拟器的协议与行为重建', 'python', False),
    'triad-isa-emulator': ('变体指令集模拟器的协议与行为重建', 'python', False),
}


PARTIAL_ANSWERS = {'glyph80-evaluator'}


def evaluator(problem, official):
    title, _, legacy = problem
    root = ROOT / title
    if official:
        return root / "答案/评测/grade.py", []
    if legacy:
        return root / "答案/compare.py", []
    return root / "题目/自测/grade.py", ["--candidate", str(root / "答案/reference")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", nargs="*", help="problem slug or folder name")
    parser.add_argument("--official", action="store_true", help="run the full evaluation suite where available")
    parser.add_argument("--language", choices=sorted({item[1] for item in PROBLEMS.values()}))
    args = parser.parse_args()
    by_title = {item[0]:slug for slug,item in PROBLEMS.items()}
    names = list(dict.fromkeys(by_title.get(name,name) for name in args.problem))
    if not names:
        names = [slug for slug,p in PROBLEMS.items() if slug not in PARTIAL_ANSWERS and (args.language is None or p[1]==args.language)
                 and (not args.official or evaluator(p, True)[0].is_file())]
    if not names:
        parser.error("No matching evaluators.")
    selected = []
    for slug in names:
        if slug not in PROBLEMS:
            parser.error(f"Unknown problem: {slug}")
        problem = PROBLEMS[slug]
        if args.language and args.language != problem[1]:
            parser.error(f"Wrong language for {slug}: {problem[1]}")
        path, options = evaluator(problem,args.official)
        if not path.is_file():
            parser.error(f"No requested suite for {slug}")
        selected.append((slug,problem[0],path,options))
    failed = []
    for slug,title,path,options in selected:
        print(f"\n[{title}]",flush=True)
        result=subprocess.run([sys.executable,"-B",str(path),*options],cwd=ROOT/title,check=False)
        if result.returncode:
            failed.append(slug)
    print(f"\nPassed {len(selected)-len(failed)}/{len(selected)} problem packages.")
    for slug in failed:
        print("FAILED",slug)
    return bool(failed)


if __name__=="__main__":
    sys.exit(main())
