# VB.NET 报表生成缓存的增量校验 / VB.NET Report-generation cache Incremental Validation

## 解析

将当前声明和最后成功回执存为两组字段。构建请求的新声明可以使旧产物过期，但不能自动把旧回执换成新凭证。

[参考实现](reference/main.vb) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Store declaration and receipt as distinct pairs. A changed declaration can make a receipt stale, but must not rewrite it to the new stamps.

The [reference implementation](reference/main.vb) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.
