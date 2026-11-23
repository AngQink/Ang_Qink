# PowerShell 发布文件清单的增量对账

**PowerShell Release Artifact Inventory Diff**

## 中文

接受 `jobs.txt`，每行指定一个任务目录。每个目录内的 `baseline.json` 将相对路径映射到小写 SHA-256。递归读取 `staging` 的普通文件并重新计算摘要。相对路径统一用 `/`。跳过含精确路径分量 `internal` 的文件及末尾为 `.tmp` 的文件，比较区分大小写。输入路径可含空格和 Unicode，路径名没有制表符或换行。

写出 `delta.tsv`。新文件为 `add<TAB>路径<TAB>新摘要`；内容改变为 `replace`；删除为 `delete<TAB>路径<TAB>-`；其余省略。按路径 Unicode 序（测试输入均为 BMP）升序。以无 BOM 的 UTF-8、LF 结束每行。无变化时生成空文件。

完成 `workspace/main.ps1`。所需工具为 PowerShell 7 和运行评测的 Python 3.11+。环境自包含，无需联网。单次构建或运行限时 90 秒，评测依据实际文件和可执行结果。

在此目录运行 `python 自测/grade.py` 检查 6 组公开任务。

## English

Accept jobs.txt with one job directory per line. Within a job, baseline.json maps relative paths to lowercase SHA-256. Recursively hash regular files in staging. Use / in normalized paths. Exclude the exact path component internal and suffix .tmp, case sensitively. Paths can include spaces and Unicode, but not tabs or newlines.

Write delta.tsv with add, path, new hash for new files; replace for changed contents; or delete, path, - for removals. Use tabs and ascending ordinal path order. Test names are in the BMP. Write UTF-8 without BOM and LF after each row. With no changes, produce an empty file.

Finish `workspace/main.ps1`. Use PowerShell 7 with Python 3.11+ to run the verifier. The workspace is self-contained and offline. Each build or process is limited to 90 seconds. Evaluation checks the actual files and executable behavior.

In this directory, run `python 自测/grade.py` for six public jobs.
