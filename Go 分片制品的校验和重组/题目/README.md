# Go 分片制品的校验和重组 / Go Checksummed Artifact Reconstruction

## 中文

接受一个参数 `jobs.txt`，每行一个任务目录。目录中有 `count.txt`，给出分片总数 n。`fragments.tsv` 每行依次为位置 i、文件名、8 位小写十六进制 CRC-32 IEEE。文件名是该目录内的普通文件。校验正确的候选才生效，同位置最后一个校验正确的候选覆盖前值。允许空分片或晚到的损坏副本。

若 0 至 n-1 都有可用分片，则按位置顺序写入 `bundle.bin`，并写 `status.txt` 为 `complete` 加 LF。若缺失任何分片，`status.txt` 写 `missing i` 加 LF，i 为最小缺失位置，且不能产生 `bundle.bin`。

完成 `workspace/main.go`。所需工具为 Go (PATH or BENCH_GO) 和运行评测的 Python 3.11+。环境自包含，无需联网。单次构建或运行限时 90 秒，评测依据实际文件和可执行结果。

在此目录运行 `python 自测/grade.py` 检查 6 组公开任务。

## English

Take one jobs.txt argument containing one job directory per line. Its count.txt gives the number of fragments n. The fragments.tsv rows contain index, filename and eight lowercase hex digits of CRC-32 IEEE. Inputs name ordinary files in the job directory. Only checksum-valid rows participate. The last valid row for a position wins. Empty fragments and corrupt late copies are allowed.

When positions 0 through n-1 are available, concatenate their exact bytes in order into bundle.bin and write complete plus LF to status.txt. Otherwise do not create bundle.bin, and write missing i plus LF using the first absent index.

Finish `workspace/main.go`. Use Go (PATH or BENCH_GO) with Python 3.11+ to run the verifier. The workspace is self-contained and offline. Each build or process is limited to 90 seconds. Evaluation checks the actual files and executable behavior.

In this directory, run `python 自测/grade.py` for six public jobs.
