# 八十位浮点求值器的字节级兼容

**Byte-Exact Compatibility for an 80-Bit Floating-Point Evaluator**

## 当时的提交

[提交源码](reference/glyph80.py)来自原对局的 ChatGPT 答案压缩包。

**部分解。** 实际复跑为 **4/5** 组原始公开样例。保留了当时的部分解。实现将有效数、指数与符号分开处理，并模拟扩展精度舍入和打印格式。部分 x87 超越函数的近似尾数仍与原工具有差异。公开三角函数样例的输出仍有差异。

从题目总目录运行以下命令可重现公开样例结果。

```powershell
python 题目/自测/grade.py --candidate 答案/reference
```

## Archived submission

The [submitted source](reference/glyph80.py) is the file from the original ChatGPT contest answer archive.

**Partial solution.** The recorded rerun is **4/5** original public samples. The archived partial submission models the sign, exponent, and significand explicitly, with extended-precision rounding and formatting. The last bits of some x87 transcendental results still differ from the original. The public small-trigonometry sample still differs.

Run the command above from the problem directory to reproduce the public-sample result.

Submission SHA-256: `299bd905d729dfce41c48885ceadeb1b894bf6844ae8afe4cc5e1ff418e4536a`
