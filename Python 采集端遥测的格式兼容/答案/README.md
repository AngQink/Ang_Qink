# Python 采集端遥测的格式兼容 / Python Collector telemetry Format Compatibility

## 解析

先减去偏移 `(previous×13 + sequence×11 + key + 17) mod 2048`，然后乘 683 并模 2,048。结果必须小于 1,024。字段按 kind → reading+16 → flag 排列，基数依次按字段取 8、32、4。验证 `(word×3 + previous + sequence×7 + key×13 + 17) mod 251` 后，才将该键滚动状态更新为 `(previous+word+checksum) mod 2048`。

[参考实现](reference/main.py) 使用题目要求的语言。[完整评测](评测/grade.py) 检查 60 组冻结场景，其中 6 组随题公开。判据包含同键连续操作、跨键交错和重置后恢复等边界。构建和执行均使用临时目录。

```powershell
python 答案/评测/grade.py
python 答案/评测/grade.py --candidate 题目/workspace --output report
```

## Solution

Subtract `(previous×13 + sequence×11 + key + 17) mod 2048`, multiply by 683 and reduce modulo 2,048. The result must be below 1,024. The field order is kind → reading+16 → flag, with bases 8, 32 and 4 for the respective fields. Only if `(word×3 + previous + sequence×7 + key×13 + 17) mod 251` matches, advance that key's state to `(previous+word+checksum) mod 2048`.

The [reference implementation](reference/main.py) uses the requested language. The [evaluator](评测/grade.py) checks 60 frozen scenarios, including all six public scenarios. It checks complete outputs across sequences, interleaved keys, and session resets. The build and execution take place in a temporary directory.

[生产器源码 / Producer source](reference/producer.c)
