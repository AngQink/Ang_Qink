# 数值表达式求值器的字节级兼容

**Byte-Exact Compatibility for a Numeric Expression Evaluator**

## 当时的提交

[提交源码](reference/glyph.py)来自原对局的 ChatGPT 答案压缩包。

**公开样例通过。** 实际复跑为 **5/5** 组原始公开样例。原实现分别还原词法与表达式求值、64 位整数回绕和旧版浮点格式化。浮点幂运算部分采用扩展精度近似。历史差分记录在 27,184 项混合检查中记有 12 项已知差异。

从题目总目录运行以下命令可重现公开样例结果。

```powershell
python 题目/自测/grade.py --candidate 答案/reference
```

## Archived submission

The [submitted source](reference/glyph.py) is the file from the original ChatGPT contest answer archive.

**Public samples pass.** The recorded rerun is **5/5** original public samples. The submission reconstructs tokenization, expression evaluation, 64-bit integer wraparound, and legacy floating-point formatting. It approximates some extended-precision power operations. The historical differential log recorded 12 mismatches in 27,184 mixed checks.

Run the command above from the problem directory to reproduce the public-sample result.

Submission SHA-256: `0cec9e878d7ead8972849ec010c71bd2b23ea61cab432cee29ac30b5b73767d4`
