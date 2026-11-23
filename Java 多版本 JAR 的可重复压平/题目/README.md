# Java 多版本 JAR 的可重复压平

**Java Reproducible Flattening of Multi-Release JARs**

## 中文

接受一个参数 `jobs.tsv`。每行给出目标 Java 版本、原 JAR 文件名和输出 JAR 文件名。相对路径基于任务清单目录。读入原 ZIP 成员。普通成员版本为 0，`META-INF/versions/N/路径` 表示版本 N 的候选，N 至少为 9。每个逻辑路径取不超过目标版本的最高项。忽略目录、原清单和未选版本。输入路径为 ASCII，候选对（路径、版本）无重复。

输出 `META-INF/MANIFEST.MF` 为首项，内容字节是 `Manifest-Version: 1.0\r\nMain-Class: Greeting\r\n\r\n`。之后按逻辑路径 ASCII 字典序写入每个选中的成员。成员必须为 STORED，ZIP 时间为 1980-01-01 00:00:00，内容逐字节保持。结果 JAR 可直接用 `java -jar` 启动，`Greeting` 会读取压平后的 notice.txt。

完成 `workspace/Main.java`。所需工具为 JDK 17+ 和运行评测的 Python 3.11+。环境自包含，无需联网。单次构建或运行限时 90 秒，评测依据实际文件和可执行结果。

在此目录运行 `python 自测/grade.py` 检查 6 组公开任务。

## English

Receive jobs.tsv with target Java version, input JAR and output JAR on each tab-separated line. Paths are relative to the job list. Base members have version 0. META-INF/versions/N/path supplies a versioned candidate, with N at least 9. For each logical path, choose the highest release no greater than the target. Ignore directories, the old manifest, and unselected versions. Inputs have ASCII names and unique (path, version) pairs.

Write META-INF/MANIFEST.MF first, with exact bytes Manifest-Version: 1.0\r\nMain-Class: Greeting\r\n\r\n. Write the remaining selected entries in ASCII path order. Every entry is STORED with ZIP timestamp 1980-01-01 00:00:00 and unmodified selected bytes. java -jar must run Greeting and read the flattened notice.txt.

Finish `workspace/Main.java`. Use JDK 17+ with Python 3.11+ to run the verifier. The workspace is self-contained and offline. Each build or process is limited to 90 seconds. Evaluation checks the actual files and executable behavior.

In this directory, run `python 自测/grade.py` for six public jobs.
