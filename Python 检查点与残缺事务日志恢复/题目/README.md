# Python 检查点与残缺事务日志恢复

**Python Recovery from Checkpoints and Torn Journals**

## 中文

接受一个参数 `jobs.txt`，其中每行指定待恢复的子目录。每个目录有 `checkpoint.json` 和 `journal.jsonl`。检查点含整数 `revision` 与键到整数的对象 `items`。日志从检查点下一版本起按顺序记录 `begin`、零条或多条 `set` / `del` 和 `commit`。开始和提交记录含 `revision`，两者都必须等于上一次提交版本加 1。修改记录含 `key`，设置还含 `value`。同一个键以事务内最后一次修改为准。读取到没有换行符的记录、非法 JSON、命令次序不合法或版本不匹配时，停止读取并丢掉当前未提交事务。`del` 删除不存在的键时无副作用。

每个子目录生成 `recovered.json`，内容是恢复后的同结构 JSON。以 UTF-8 保存，按键排序，去掉分隔符旁空格，并以单个 LF 结束。应先生成临时文件再替换目标，保留检查点与日志的原始字节。

完成 `workspace/recover.py`。所需工具为 Python 3.11+ 和运行评测的 Python 3.11+。环境自包含，无需联网。单次构建或运行限时 90 秒，评测依据实际文件和可执行结果。

在此目录运行 `python 自测/grade.py` 检查 6 组公开任务。

## English

Accept a jobs.txt path, with one subdirectory per line. Each directory contains checkpoint.json and journal.jsonl. A checkpoint holds an integer revision and an items object mapping keys to integers. A transaction consists of begin, zero or more set/del records, and commit. Both begin and commit carry revision, exactly one greater than the last committed revision. Writes carry key; set adds value. The last write for a key in the transaction wins. At an unterminated line, malformed JSON, invalid operation order, or wrong revision, stop at that point and discard the open transaction. Deleting a missing key has no effect.

Write recovered.json in each job directory. Preserve the checkpoint schema, sort object keys, omit separator whitespace, use UTF-8 and a single terminal LF. Stage the file before replacement and preserve the original inputs.

Finish `workspace/recover.py`. Use Python 3.11+ with Python 3.11+ to run the verifier. The workspace is self-contained and offline. Each build or process is limited to 90 seconds. Evaluation checks the actual files and executable behavior.

In this directory, run `python 自测/grade.py` for six public jobs.
