# 二次相位函数的约束求和 / Constrained Quadratic Phase Sums

实现一个在线处理命令的程序，维护二进制变量上的二次相位函数，并在给定线性约束下计算精确的复数求和结果。程序需要支持函数更新、快照、点值及快照间重叠查询。

入口为 `phase.py`。测试环境为 Windows 与 CPython 3.14.2，仅使用 Python 标准库。

## 1. 数学对象

固定n个二进制变量x[0],...,x[n-1]，每项为0或1。当前函数为：

`q(x) = c + sum(l[u]*x[u]) + 2*sum(x[u]*x[v] : {u,v} is an edge)  (mod 4)`。

c与每个l[u]在0..3内，边是无自环、无重边的无向图。
函数值q(x)用0..3表示。令i为虚数单位，i^0=1、i^1=i、i^2=-1、i^3=-i。

查询在给定二进制线性条件下，对每一个不同的合法x恰好求和一次：

`Z = sum(i^q(x) : A*x = b over GF(2))`。

Z是**复数之和**。不同x的贡献可能相消；存在合法x不代表Z非零。
没有概率采样、浮点误差容忍、绝对值化或归一化因子。

## 2. 协议与限制

输入输出是UTF-8 NDJSON，每行一个JSON对象，所有输入保证合法。
每读一条命令就必须立即输出并flush一条响应，不能等EOF。stdout只写响应，行尾LF；stderr为空，EOF退出码0。
字段顺序与分隔空格不限，字段集合、值与类型必须准确。整数不接受浮点数、字符串或布尔替代。

- 第一条且仅第一条为init；`0 <= n <= 512`，进程中固定。
- 初始 constant 字段与 linear 数组各项为0..3的整数；edges是合法简单图，每边出现一次，端点顺序任意。
- delta是有符号64位整数，更新按模4进行，负值也正常取模。
- u、v、dst、src为有效变量下标。cz及xor的两个下标保证不同；swap允许相同。
- 快照slot为0..63；load和overlap引用的快照保证已经保存。
- 每个a是最多128个十六进制字符串的数组，每个字符串表示0..2^n-1的非负整数；允许前导零及大小写，不带符号或0x前缀。
- 每个mask的**第u个二进制位**对应变量x[u]，该行条件为mask中所有变量的异或等于b对应项。
- b与a等长，项为整数0或1；零mask和重复/冗余条件都合法。
- 每进程最多20,000条命令；ask与overlap合计最多256条。
- 每个完整场景30秒、峰值工作集512 MiB；在线交互每条最多等待5秒。
- 运行时间包含解释器启动、JSON输入输出与计算，不包括测试输入的准备时间。

实现须集中在 `phase.py`。除标准库正常导入与本文件外，不读取其他文件、不创建持久化文件、不联网、不启动子进程、不使用ctypes或加载DLL。
允许使用通用缓存。程序需要正确处理全部满足约束的输入；公开测试仅用于自测。

## 3. 初始化

```json
{"op":"init","n":2,"linear":[0,0],"edges":[[0,1]],"constant":0}
```

建立q，清空快照。响应 `{"ok":true}`。

## 4. 更新当前函数

以下命令响应 `{"ok":true}`。

| 命令 | 含义 |
|---|---|
| `{"op":"phase","u":u,"delta":d}` | q(x)增加d*x[u]，模4 |
| `{"op":"global","delta":d}` | q(x)整体增加常数d，模4；全局相位必须保留 |
| `{"op":"cz","u":u,"v":v}` | q(x)增加2*x[u]*x[v]，即切换该边 |
| `{"op":"flip","u":u}` | 新函数q'(x)=q(y)，其中y[u]=x[u] XOR 1，其余y[j]=x[j] |
| `{"op":"xor","dst":u,"src":v}` | 新函数q'(x)=q(y)，其中y[u]=x[u] XOR x[v]，其余y[j]=x[j] |
| `{"op":"swap","u":u,"v":v}` | 在q的输入中交换这两个变量 |

flip/xor/swap是对**当前函数的输入替换**，不改变之后查询条件所用的坐标编号，也不改变n。
上述替换后的函数仍具有第1节的形式。所有表达式都读取该命令执行前的函数。
不能把xor误解为交换变量、增加函数值、修改某个固定输入样本或改写之后输入的约束行。

## 5. 快照

```json
{"op":"save","slot":3}
{"op":"load","slot":3}
```

save保存当前函数的值，覆盖该slot先前的快照；load把当前函数替换为指定快照的值。
后续更新不改变已有快照。load后再更新也不改变快照。保存和加载都响应 `{"ok":true}`。

## 6. ask：受限相位和

```json
{"op":"ask","a":["3"],"b":[1]}
```

先求满足线性条件的集合S。

若S为空，只输出 `{"possible":false}`，没有其他字段。

若S非空，响应恰好为：

```text
{"possible":true,"free":r,"first":s,"amplitude":T}
```

- r是S的仿射维数，所以S恰好有2^r个不同输入。
- s是S中字典序最小的长度n二进制字符串。**字符串第0项是x[0]**，然后是x[1]，以此类推；比较时'0'小于'1'，不是把mask作为一个整数取最小值。
- T编码Z。若Z=0，T恰好为 `{"zero":true}`。
- 若Z非零，T恰好为 `{"zero":false,"power":k,"phase":p}`，含义为：

`Z = 2^(k/2) * exp(i*pi*p/4)`。

k为0..2*r的整数，p为0..7的整数。**power是二倍的二进制幅度指数**，允许奇数；phase用八分之一整圈为单位。
本题的非零和都具有此形式，编码唯一。不能只返回|Z|、Z的实部、概率或内部实现的计数。

约束有解且Z=0时仍必须返回possible=true、free、first和zero=true。
n=0且无矛盾条件时，S只包含空输入：free=0，first=""，Z=i^c。

## 7. overlap：快照间的未归一化重叠

```json
{"op":"overlap","left":0,"right":1,"a":[],"b":[]}
```

只查询快照，不改变当前函数或快照。响应格式与ask相同，但求和项为：

`Z = sum(i^(q_left(x)-q_right(x)) : A*x=b over GF(2))`。

减法方向必须正确。交换left与right应使非零结果共轭。
同一个快照与自身重叠时，每项都是1；若条件可行，Z=2^r，对应power=2*r、phase=0。
没有2^(-n)或其他归一化因子；当前函数的值不参与这个查询。

## 8. value：点值

```json
{"op":"value","bits":"01"}
```

bits恰好n个0/1字符，第u项为x[u]。响应 `{"phase":v}`，v为当前q(x)在0..3中的值。
这里phase表示i的指数，单位是四分之一整圈；它与amplitude中phase的八分之一整圈单位不同。

## 9. 例子

1. n=1，q(x)=x，无条件：Z=1+i，free=1、first="0"，amplitude为 `{"zero":false,"power":1,"phase":1}`。
2. n=1，q(x)=2*x，无条件：两个输入贡献1和-1，possible=true、free=1、first="0"，amplitude为 `{"zero":true}`。
3. n=2，q(x)=2*x[0]*x[1]，无条件：四个贡献为1,1,1,-1，Z=2，对应power=2、phase=0，而不是power=4。
4. n=2，条件mask="3"、rhs=1表示x[0] XOR x[1]=1，最小字符串为"01"，不是"10"。

## 10. 完整样例

输入：

```json
{"op":"init","n":1,"linear":[1],"edges":[],"constant":0}
{"op":"ask","a":[],"b":[]}
{"op":"save","slot":0}
{"op":"phase","u":0,"delta":1}
{"op":"ask","a":[],"b":[]}
{"op":"overlap","left":0,"right":0,"a":[],"b":[]}
{"op":"ask","a":["0"],"b":[1]}
```

输出：

```json
{"ok":true}
{"possible":true,"free":1,"first":"0","amplitude":{"zero":false,"power":1,"phase":1}}
{"ok":true}
{"ok":true}
{"possible":true,"free":1,"first":"0","amplitude":{"zero":true}}
{"possible":true,"free":1,"first":"0","amplitude":{"zero":false,"power":2,"phase":0}}
{"possible":false}
```

## 11. 公开测试

只需完成 `phase.py`；程序从标准输入逐行读取命令，向标准输出逐行写出响应。每条命令均须在收到后立即响应并刷新输出缓冲区。

在本题目录运行以下命令。

```text
python -B -m unittest discover -s public_tests -v
```

随附 13 个公开测试，覆盖样例、相消、全局相位、变量替换、快照、约束解的字典序以及在线响应等基础行为。程序仍须满足正文的全部数据范围和资源限制。
