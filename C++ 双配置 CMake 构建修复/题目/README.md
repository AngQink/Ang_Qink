# C++ 双配置 CMake 构建修复

**C++ Dual-Profile CMake Build Repair**

## 中文

修复 `CMakeLists.txt`，令原 C++ 工作区支持 Ninja 的两次独立配置。选项 `BENCH_CHANNEL` 可为 `Stable` 或 `Canary`。从 `cmake/contract.hpp.in` 生成构建目录的头文件，设定 ABI、步幅、负值截断选项。Stable 对应 29、19、1，Canary 对应 43、31、0。将 `src/receipt.cpp` 编译为库并链接到可执行目标 `receipt`。保持随附源码不变。

构建后的程序接收整数对 stamp、delta，打印 stamp、处理后 delta、ABI 和 `(stamp×步幅+delta) mod 997`。Stable 将负 delta 截为 0，Canary 保留负值。正式评测会实际配置、构建和运行两份目标，检查各自的生成头与链接行为。

完成 `workspace/CMakeLists.txt`。所需工具为 CMake, Ninja and G++ 和运行评测的 Python 3.11+。环境自包含，无需联网。单次构建或运行限时 90 秒，评测依据实际文件和可执行结果。

在此目录运行 `python 自测/grade.py` 检查 6 组公开任务。

## English

Repair CMakeLists.txt for two independent Ninja configurations. BENCH_CHANNEL is Stable or Canary. Configure the header template into the build tree with ABI, stride, and negative-value clamp. Stable uses 29, 19, 1. Canary uses 43, 31, 0. Compile src/receipt.cpp as a library, link it into executable target receipt, and keep the supplied C++ sources unchanged.

The executable takes integer pairs stamp and delta and emits stamp, adjusted delta, ABI, and (stamp×stride+delta) mod 997. Stable clamps negative delta to zero, while Canary preserves it. The full suite configures, builds, and executes both profiles.

Finish `workspace/CMakeLists.txt`. Use CMake, Ninja and G++ with Python 3.11+ to run the verifier. The workspace is self-contained and offline. Each build or process is limited to 90 seconds. Evaluation checks the actual files and executable behavior.

In this directory, run `python 自测/grade.py` for six public jobs.
