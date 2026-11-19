# 模二的幂的二次同余计数 / Counting Solutions to Quadratic Congruences Modulo Powers of Two

本页定义子协议。组合后的入口、命令前缀、资源配额及自测方式见[总题面](../../README.md)。

维护模 2 的幂的二次式，在变量低位受限时精确计数并寻找规范解。

## 1. 二次式与定义域

固定变量个数d和位数k，所有变量x_i取0..2^k-1的整数。维护多项式：

```text
F(x) = constant + sum(linear[i]*x_i)
       + sum(q[i][i]*x_i*x_i)
       + sum(q[i][j]*x_i*x_j, i<j)     (mod 2^k)
```

q是d×d**上三角系数表**，下三角保证为0。每个交叉项只算一次，不再乘2。对角项是平方项。系数和constant可以为负，全部按模2^k解释。

查询给出target，以及每个变量的低位约束[r_i,a_i]：

```text
x_i mod 2^r_i = a_i
0 <= r_i <= k
0 <= a_i < 2^r_i
```

r_i=0时a_i只能为0，表示没有锁定位；r_i=k时变量完全确定。各变量锁定位数可以不同。求满足所有低位约束、且F(x)=target (mod 2^k)的不同完整向量个数。

计数是**精确非负整数，不取模**，可能远超64位。每个完整向量只算一次。

## 2. 规范解的顺序

对向量x构造长度d*k的0/1序列，按“低位先、同一位内变量编号先”的顺序：

```text
bit0(x_0), bit0(x_1), ..., bit0(x_(d-1)),
bit1(x_0), bit1(x_1), ..., bit1(x_(d-1)),
...
bit(k-1)(x_0), ..., bit(k-1)(x_(d-1))
```

bit0是最低有效位。规范解是所有满足查询的向量中，上述序列按0<1取字典序最小者。锁定的位仍出现在序列里，但所有候选在这些位上相同。

这一定义不是按整数向量作通常的字典序，也不是先比较x_0的所有位再比较x_1。位序由上面的循环次序精确定义。

## 3. 协议、环境和限制

UTF-8 NDJSON，每行一条合法JSON命令；每读一条立即回复一行并flush，不等EOF。stdout仅含响应，LF行尾，stderr为空，EOF退出0。允许忽略空白输入行。

字段顺序和空格不限；响应字段集合、精确类型、值与数组顺序必须匹配。整数不能由浮点数、字符串、布尔代替，不接受重复JSON字段。

- 基准环境为 Windows / CPython 3.14.2。将解法写在 `veil.py` 中，仅使用 Python 标准库。
- 1<=d<=16，1<=k<=40，在进程中固定。
- 初始系数及quad/linear/constant更新的value为-2^63..2^63-1整数，允许负数及相差2^k倍数的不同表示。
- 每进程最多5000条命令，其中solve最多64条，且witness=true的solve最多8条（无论是否可行）。
- 每进程60秒、峰值工作集512 MiB；每条在线响应最多5秒。计时包括启动、计算、输入输出。

除本文件及正常标准库导入外，不读取其他文件、不创建持久化文件、不联网、不启动子进程、不用ctypes或调用外部EXE/DLL。允许通用缓存。

## 4. init

第一条且仅第一条命令：

```json
{"op":"init","variables":2,"bits":3,
 "q":[[1,1],[0,1]],"linear":[0,0],"constant":0}
```

variables为d，bits为k；q为d×d上三角表，linear长度d。下三角元素为0。初始化清空快照。响应 `{"ok":true}`。

本例F(x)=x_0^2+x_0*x_1+x_1^2 (mod 8)。

## 5. 修改与快照

以下命令均响应 `{"ok":true}`：

```json
{"op":"quad","i":0,"j":1,"value":-3}
{"op":"linear","i":1,"value":7}
{"op":"constant","value":-1}
{"op":"save","slot":31}
{"op":"load","slot":31}
```

- quad：将q[i][j]设为value，保证0<=i<=j<d。i=j改平方项；i<j改一个交叉项。
- linear：将linear[i]设为value。
- constant：修改常数项。
- save：复制保存全部q、linear、constant，覆盖slot旧快照。
- load：恢复该快照。slot为0..31，保证已保存。之后的修改、其他槽及再次load不改变已保存快照。

查询和缓存不改变多项式或快照。d、k不变。系数仅按模2^k参与计算，相差2^k倍数的更新具有相同数学语义。

## 6. solve

```json
{"op":"solve","target":1,"locks":[[0,0],[2,1]],"witness":true}
```

target为0..2^k-1整数。locks长度恰为d，每项[r_i,a_i]的含义见第1节；witness是JSON布尔，表示是否请求规范解。

响应字段恰为：

```text
{"possible":P,"count":N,"witness":null or {"values":[...],"sha256":H}}
```

- possible为JSON布尔，等价于精确count>0。
- count是完整解向量的精确数量，JSON整数；不可行时为0。
- 不可行时witness=null。
- 可行且请求witness=false时，仍返回witness=null；这不表示不可行。
- 可行且请求witness=true时，返回第2节规范解的values和哈希。values长度d，按变量编号排列，每项是0..2^k-1整数。不是返回位序列，也不是某个变换后的坐标。

即使锁定位很多，也必须按**不同原始完整向量**计数，不能重复计入相同向量的其他参数表示。

## 7. 见证哈希

对以下字节串取SHA256，输出64个小写十六进制字符：

```text
b"DYAD1"                             # 5 ASCII bytes, no NUL or newline
+ bytes([d,k])                       # one byte each: variable count, then bit width
+ concat(x_i.to_bytes((k+7)//8,"little") for i=0..d-1)
```

每个变量使用相同的固定宽度ceil(k/8)字节，无符号小端；不足整字节时最高字节的无用高位为0。不编码多项式、锁定信息、count、分隔符或十进制字符串。

## 8. 语义例子

1. d=1,k=4,F(x)=x^2,target=9，无锁：解为3、5、11、13，count=4。最低位先比较，规范解是5。
2. d=2,k=2,F=x_0+2*x_1,target=2，无锁：count=4，规范解[2,0]。按位平面比较时，x_1的bit0先于x_0的bit1。
3. d=2,k=3,F=x_0*x_1,target=0，无锁：count=20，规范解[0,0]。
4. d=2,k=3,F=x_0^2+x_0*x_1+x_1^2：target=2无解；target=1有12个解；target=0有4个解。
5. d=1,k=4,F=x^2+x：target=2有2个解，target=3无解。
6. 零多项式、target=0时，count=2^(sum(k-r_i))，规范解就是各个给定a_i，其他位都取0。
