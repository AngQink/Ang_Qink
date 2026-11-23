# Rust 本地依赖的 Cargo 特性修复 / Rust Cargo Feature Resolution with Local Dependencies

## 中文

修复根 Cargo.toml，在离线模式下分别执行 `cargo build --offline --no-default-features --features baseline` 和 `cargo build --offline --no-default-features --features next`。两次构建都要生成 `receipt`。所有依赖都来自随附的本地路径，保持 Rust 源码与两个依赖清单不变。

`baseline` 联动 `wire/legacy`、`policy/legacy`，`next` 联动对应的 `modern` 特性。每次只允许一种 wire 特性。成功构建后程序读入 stamp、delta，并输出 stamp、处理后 delta、ABI 和凭证。baseline 截断负值，ABI 29，步幅 19；next 保持负值，ABI 43，步幅 31。凭证为 `(stamp×步幅+处理后delta) mod 997` 的非负余数。

完成 `workspace/Cargo.toml`。所需工具为 Cargo and rustc 和运行评测的 Python 3.11+。环境自包含，无需联网。单次构建或运行限时 90 秒，评测依据实际文件和可执行结果。

在此目录运行 `python 自测/grade.py` 检查 6 组公开任务。

## English

Repair the root Cargo.toml so offline builds with --no-default-features --features baseline and --features next both produce receipt. All dependencies are local. Keep the supplied Rust sources and dependency manifests unchanged.

Forward baseline to wire/legacy and policy/legacy, and next to the two modern features. Exactly one wire feature is allowed per build. The executable takes stamp and delta and outputs stamp, adjusted delta, ABI, and a receipt token. Baseline clamps negative delta, with ABI 29 and stride 19. Next preserves negative delta, with ABI 43 and stride 31. The token is the nonnegative remainder of (stamp×stride+adjusted delta) modulo 997.

Finish `workspace/Cargo.toml`. Use Cargo and rustc with Python 3.11+ to run the verifier. The workspace is self-contained and offline. Each build or process is limited to 90 seconds. Evaluation checks the actual files and executable behavior.

In this directory, run `python 自测/grade.py` for six public jobs.
