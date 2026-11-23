# Windows Batch 安装事件帧的格式兼容 / Windows Batch Installation event frames Format Compatibility

## 解析

先减去偏移 `(previous×29 + sequence×43 + key + 33) mod 2048`，然后乘 1463 并模 2,048。结果必须小于 1,024。字段按 flag → kind → reading+16 排列，基数依次按字段取 8、32、4。验证 `(word×19 + previous + sequence×7 + key×29 + 33) mod 251` 后，才将该键滚动状态更新为 `(previous+word+checksum) mod 2048`。

[参考实现](reference/main.cmd) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Subtract `(previous×29 + sequence×43 + key + 33) mod 2048`, multiply by 1463 and reduce modulo 2,048. The result must be below 1,024. The field order is flag → kind → reading+16, with bases 8, 32 and 4 for the respective fields. Only if `(word×19 + previous + sequence×7 + key×29 + 33) mod 251` matches, advance that key's state to `(previous+word+checksum) mod 2048`.

The [reference implementation](reference/main.cmd) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.

[生产器源码 / Producer source](reference/producer.c)
