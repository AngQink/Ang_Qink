# 答案包 / Answer Package

## 中文

每题包括中英文解析和参考实现。解析说明状态表示、核心推导、正确性依据和容易漏掉的边界。公开测试、样例及资源判据在题目包内。

把两个 ZIP 解压到同一目录后，运行：

    python -m pip install pytest
    python compare.py

pytest 用于事务键值库和二进制账本。其他题目的测试只用标准库。可将一个或多个题目目录名跟在命令后面，只运行指定题。对照运行在临时目录中。

## English

Each solution includes a bilingual explanation and a reference implementation. The explanations cover state representation, the main algorithm, its correctness rationale, and important boundary cases. The question package contains public tests, examples, and resource criteria.

After extracting both ZIP files into the same directory, run:

    python -m pip install pytest
    python compare.py

The transactional key-value store and binary ledger use pytest. The other test suites use the Python standard library. Pass one or more problem directory names to run a subset. The comparison uses temporary copies.
